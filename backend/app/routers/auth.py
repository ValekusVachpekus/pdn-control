"""Регистрация / логин по email+password + OAuth-заглушки (Яндекс/ВК).

Реальный OAuth-flow (редирект → провайдер → callback → JWT) — отдельная задача:
здесь возвращаем 501 c понятным сообщением, чтобы это нельзя было перепутать
с рабочим эндпоинтом. Конструкция сохраняет контракт с фронтом — когда OAuth
будет готов, поменяем только тело функции.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import get_settings
from ..db import get_session
from ..models.email_code import EmailCode
from ..models.user import User
from ..plans import POLICY_VERSION
from ..schemas.auth import (
    AuthOut,
    LoginIn,
    OAuthIn,
    RegisterIn,
    RequestCodeIn,
    UserOut,
    VerifyCodeIn,
)
from ..services import otp
from ..services.auth import create_access_token, hash_password, verify_password
from ..services.email import send_otp_email
from ..services.rate_limit import allow_otp_request

router = APIRouter(prefix="/api/auth", tags=["auth"])

_OAUTH_PROVIDERS = {"yandex", "vk"}


def _client_ip(request: Request) -> str:
    """IP клиента с учётом reverse-proxy (Caddy ставит X-Forwarded-For)."""
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


@router.post("/register", response_model=AuthOut, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterIn, session: AsyncSession = Depends(get_session)) -> AuthOut:
    # 152-ФЗ ст. 9: без согласия — не регистрируем.
    if not body.consent:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="consent to personal data processing is required",
        )

    existing = await session.scalar(select(User).where(User.email == body.email.lower()))
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="email already registered")

    user = User(
        email=body.email.lower(),
        password_hash=hash_password(body.password),
        consent_at=datetime.now(timezone.utc),
        consent_policy_version=POLICY_VERSION,
    )
    session.add(user)
    await session.flush()  # чтобы получить user.id до коммита

    token = create_access_token(user.id)
    return AuthOut(token=token, user=UserOut.model_validate(user))


@router.post("/login", response_model=AuthOut)
async def login(body: LoginIn, session: AsyncSession = Depends(get_session)) -> AuthOut:
    user = await session.scalar(select(User).where(User.email == body.email.lower()))
    # Одинаковая 401 на «нет такого юзера» и «не тот пароль» — не утекает наружу,
    # есть ли аккаунт с таким email. OAuth-юзеров (без password_hash) тоже не пускаем.
    if (
        user is None
        or user.password_hash is None
        or not verify_password(body.password, user.password_hash)
    ):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")

    token = create_access_token(user.id)
    return AuthOut(token=token, user=UserOut.model_validate(user))


@router.post("/request-code", status_code=status.HTTP_204_NO_CONTENT)
async def request_code(
    body: RequestCodeIn, request: Request, session: AsyncSession = Depends(get_session)
) -> Response:
    """Шаг 1 passwordless-входа: генерим 6-значный код, кладём его ХЭШ с TTL и
    шлём письмо. Всегда отвечаем 204 — наличие аккаунта не раскрываем
    (анти-enumeration). Rate-limit по e-mail и IP против спам-рассылки.
    """
    email = body.email.lower()
    s = get_settings()

    # Rate-limit срабатывает молча (тоже 204), чтобы не утекал тайминг/факт лимита.
    if allow_otp_request(email, _client_ip(request)):
        # Инвалидируем прежние живые коды этого e-mail — действителен только новый.
        await session.execute(
            update(EmailCode)
            .where(EmailCode.email == email, EmailCode.used.is_(False))
            .values(used=True)
        )
        code = otp.generate_code()
        session.add(EmailCode(
            email=email,
            code_hash=otp.hash_code(code),
            expires_at=datetime.now(timezone.utc) + timedelta(seconds=s.otp_ttl_sec),
        ))
        await session.flush()
        await send_otp_email(email, code)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/verify-code", response_model=AuthOut)
async def verify_code(
    body: VerifyCodeIn, session: AsyncSession = Depends(get_session)
) -> AuthOut:
    """Шаг 2: проверяем код, выдаём JWT. Находим/создаём пользователя. При первой
    регистрации (юзера нет) consent обязателен — 152-ФЗ ст. 9.
    """
    email = body.email.lower()
    now = datetime.now(timezone.utc)
    # Одинаковая 400 на «нет кода» и «неверный код» — не раскрываем наличие аккаунта.
    invalid = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="invalid or expired code"
    )

    ec = await session.scalar(
        select(EmailCode)
        .where(EmailCode.email == email, EmailCode.used.is_(False))
        .order_by(EmailCode.created_at.desc())
        .limit(1)
    )
    if ec is None or not otp.is_consumable(ec, now):
        raise invalid

    if not otp.code_matches(body.code, ec.code_hash):
        # Учитываем неудачную попытку отдельным коммитом: иначе rollback get_session
        # на HTTPException откатил бы инкремент и брутфорс-лимит не работал бы.
        ec.attempts += 1
        await session.commit()
        raise invalid

    ec.used = True  # код одноразовый

    user = await session.scalar(select(User).where(User.email == email))
    if user is None:
        if not body.consent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="consent to personal data processing is required",
            )
        user = User(
            email=email,
            consent_at=now,
            consent_policy_version=POLICY_VERSION,
        )
        session.add(user)
        await session.flush()

    token = create_access_token(user.id)
    return AuthOut(token=token, user=UserOut.model_validate(user))


@router.post("/oauth/{provider}", response_model=AuthOut)
async def oauth_login(
    provider: str,
    body: OAuthIn,
    session: AsyncSession = Depends(get_session),  # noqa: ARG001 — будет нужен после реализации
) -> AuthOut:
    """Заглушка OAuth.

    Реальный flow: фронт → /api/auth/oauth/{provider} → redirect к Яндексу/ВК →
    callback → обмен code на access_token → достаём email → ищем/создаём User →
    выдаём JWT. Сейчас не реализовано — отдаём 501.
    """
    if provider not in _OAUTH_PROVIDERS:
        raise HTTPException(status_code=404, detail="unknown provider")
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=f"OAuth via {provider} is not implemented yet. Use /api/auth/register.",
    )
