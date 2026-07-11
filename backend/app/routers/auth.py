"""Аутентификация: email+password, passwordless OTP по коду и соц-вход OAuth.

Соц-вход (Яндиз/ВК) — реальный redirect authorization-code flow (#72):
GET /oauth/{provider}/start → редирект к провайдеру; GET /oauth/{provider}/callback
→ обмен code на токен, профиль, find-or-create User, httpOnly-JWT, редирект в SPA.
Провайдерская механика — в services/oauth.py; включается заданием client_id/secret.
"""
from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import get_settings
from ..db import get_session
from ..deps import get_current_user
from ..models.email_code import EmailCode
from ..models.user import User
from ..plans import POLICY_VERSION
from ..schemas.auth import (
    AuthOut,
    ConfirmRegisterIn,
    LoginIn,
    RegisterIn,
    RequestCodeIn,
    UserOut,
    VerifyCodeIn,
)
from ..services import oauth, oauth_state, otp, pending_registration
from ..services.auth import create_access_token, hash_password, verify_password
from ..services.email import send_otp_email
from ..services.rate_limit import allow_otp_request

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _client_ip(request: Request) -> str:
    """IP клиента с учётом reverse-proxy (Caddy ставит X-Forwarded-For)."""
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


async def _issue_and_send_code(session: AsyncSession, email: str) -> None:
    """Инвалидирует прежние живые коды e-mail, создаёт новый (хэш + TTL), шлёт письмо."""
    await session.execute(
        update(EmailCode)
        .where(EmailCode.email == email, EmailCode.used.is_(False))
        .values(used=True)
    )
    code = otp.generate_code()
    session.add(EmailCode(
        email=email,
        code_hash=otp.hash_code(code),
        expires_at=datetime.now(timezone.utc) + timedelta(seconds=get_settings().otp_ttl_sec),
    ))
    await session.flush()
    await send_otp_email(email, code)


async def _consume_email_code(session: AsyncSession, email: str, code: str, now: datetime) -> None:
    """Проверяет и ГАСИТ последний живой код e-mail. HTTPException 400 при
    неверном/протухшем/исчерпанном. Неудачная попытка фиксируется отдельным
    коммитом — иначе rollback get_session на 400 сбросил бы счётчик и брутфорс-
    лимит не работал бы.
    """
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
    if not otp.code_matches(code, ec.code_hash):
        ec.attempts += 1
        await session.commit()
        raise invalid
    ec.used = True  # код одноразовый


@router.post("/register", status_code=status.HTTP_202_ACCEPTED)
async def register(
    body: RegisterIn, request: Request, session: AsyncSession = Depends(get_session)
) -> dict:
    """Шаг 1 регистрации: НЕ создаём пользователя, а отправляем код подтверждения
    на e-mail. Пароль (bcrypt-хэш) и согласие держим в pending-регистрации до
    подтверждения кодом (POST /register/confirm). Так неподтверждённый аккаунт не
    существует и не может войти. 152-ФЗ ст. 9: без согласия не начинаем.
    """
    if not body.consent:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="consent to personal data processing is required",
        )
    email = body.email.lower()
    existing = await session.scalar(select(User).where(User.email == email))
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="email already registered")

    # Rate-limit отправки письма (как у request-code). При активном кулдауне
    # прежний код + pending ещё живы, поэтому подтверждение сработает по ним.
    if allow_otp_request(email, _client_ip(request)):
        pending_registration.save(email, {
            "password_hash": hash_password(body.password),
            "consent": body.consent,
        })
        await _issue_and_send_code(session, email)

    return {"status": "verification_required", "email": email}


@router.post("/register/confirm", response_model=AuthOut,
             status_code=status.HTTP_201_CREATED)
async def register_confirm(
    body: ConfirmRegisterIn, session: AsyncSession = Depends(get_session)
) -> AuthOut:
    """Шаг 2 регистрации: подтверждаем e-mail кодом и СОЗДАЁМ пользователя с
    ранее принятыми паролем и согласием. Возвращаем JWT.
    """
    email = body.email.lower()
    now = datetime.now(timezone.utc)
    await _consume_email_code(session, email, body.code, now)

    pending = pending_registration.pop(email)
    if pending is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="registration expired, please start again",
        )
    # Гонка: пользователь мог появиться между шагами.
    if await session.scalar(select(User).where(User.email == email)) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="email already registered")

    user = User(
        email=email,
        password_hash=pending["password_hash"],
        consent_at=now,
        consent_policy_version=POLICY_VERSION,
    )
    session.add(user)
    await session.flush()

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
    """Шаг 1 passwordless-ВХОДА (только для существующих аккаунтов): шлём
    6-значный код на e-mail. Всегда отвечаем 204 — наличие аккаунта не
    раскрываем (анти-enumeration). Код отправляем ТОЛЬКО если аккаунт есть:
    вход по коду — это логин, а не регистрация. Rate-limit по e-mail и IP.
    """
    email = body.email.lower()

    # Rate-limit срабатывает молча (тоже 204), чтобы не утекал тайминг/факт лимита.
    if allow_otp_request(email, _client_ip(request)):
        # Код входа шлём только зарегистрированным (незнакомым письмо не отправляем).
        user_exists = await session.scalar(select(User.id).where(User.email == email))
        if user_exists is not None:
            await _issue_and_send_code(session, email)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/verify-code", response_model=AuthOut)
async def verify_code(
    body: VerifyCodeIn, session: AsyncSession = Depends(get_session)
) -> AuthOut:
    """Шаг 2: проверяем код и выдаём JWT для СУЩЕСТВУЮЩЕГО аккаунта. Вход по
    коду — только логин: если аккаунта нет, НЕ создаём его (404), а предлагаем
    зарегистрироваться. Регистрация — отдельный осознанный поток (пароль + код
    или OAuth).
    """
    email = body.email.lower()
    now = datetime.now(timezone.utc)
    await _consume_email_code(session, email, body.code, now)

    user = await session.scalar(select(User).where(User.email == email))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="account not found, please register",
        )

    token = create_access_token(user.id)
    return AuthOut(token=token, user=UserOut.model_validate(user))


def _oauth_redirect_uri(provider: str) -> str:
    """redirect_uri колбэка — должен совпадать с зарегистрированным у провайдера."""
    return f"{get_settings().oauth_backend_base}/api/auth/oauth/{provider}/callback"


def _frontend(query: str) -> str:
    return f"{get_settings().oauth_frontend_redirect}/{query}"


def _cookie_secure() -> bool:
    # В dev по http браузер отбросил бы Secure-cookie — там его выключаем.
    return get_settings().app_env != "dev"


@router.get("/oauth/{provider}/start")
async def oauth_start(provider: str, consent: bool = False) -> RedirectResponse:
    """Шаг 1: редирект на экран согласия провайдера. `consent` — состояние
    чекбокса согласия на ПДн (нужно при первой регистрации, 152-ФЗ ст. 9).
    """
    if not oauth.is_supported(provider):
        raise HTTPException(status_code=404, detail="unknown provider")
    if not oauth.is_configured(provider):
        return RedirectResponse(_frontend("?oauth_error=provider_unavailable"), status_code=307)

    state = secrets.token_urlsafe(24)
    verifier = oauth.new_code_verifier() if oauth.uses_pkce(provider) else None
    challenge = oauth.code_challenge_s256(verifier) if verifier else None
    try:
        oauth_state.save_state(
            state, {"provider": provider, "consent": bool(consent), "code_verifier": verifier}
        )
    except Exception:  # noqa: BLE001 — Redis недоступен: без CSRF-стейта не стартуем
        return RedirectResponse(_frontend("?oauth_error=state"), status_code=307)

    url = oauth.build_authorize_url(
        provider, redirect_uri=_oauth_redirect_uri(provider),
        state=state, code_challenge=challenge,
    )
    return RedirectResponse(url, status_code=307)


@router.get("/oauth/{provider}/callback")
async def oauth_callback(
    provider: str,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    device_id: str | None = None,
    session: AsyncSession = Depends(get_session),
) -> RedirectResponse:
    """Шаг 2: провайдер вернул code+state. Валидируем state (CSRF), меняем code
    на токен, читаем профиль, находим/создаём/линкуем User, ставим httpOnly-JWT
    и возвращаем в SPA. Любая ошибка → редирект в SPA без сессии.
    """
    if not oauth.is_supported(provider):
        raise HTTPException(status_code=404, detail="unknown provider")

    # Пользователь отказал в доступе / провайдер вернул ошибку.
    if error or not code or not state:
        return RedirectResponse(_frontend("?oauth_error=denied"), status_code=307)

    saved = oauth_state.pop_state(state)
    if saved is None or saved.get("provider") != provider:
        return RedirectResponse(_frontend("?oauth_error=state"), status_code=307)

    try:
        token = await oauth.exchange_code(
            provider, code=code, redirect_uri=_oauth_redirect_uri(provider),
            code_verifier=saved.get("code_verifier"), device_id=device_id,
        )
        email, _uid = await oauth.fetch_profile(provider, token)
    except oauth.OAuthError:
        return RedirectResponse(_frontend("?oauth_error=provider"), status_code=307)

    email = email.lower()
    now = datetime.now(timezone.utc)
    user = await session.scalar(select(User).where(User.email == email))
    if user is None:
        # Первая регистрация — согласие обязательно (152-ФЗ ст. 9), иначе без сессии.
        if not saved.get("consent"):
            return RedirectResponse(_frontend("?oauth_error=consent_required"), status_code=307)
        user = User(
            email=email, oauth_provider=provider,
            consent_at=now, consent_policy_version=POLICY_VERSION,
        )
        session.add(user)
        await session.flush()
    elif user.oauth_provider is None:
        user.oauth_provider = provider  # линкуем соц-вход к существующему аккаунту

    jwt_token = create_access_token(user.id)
    resp = RedirectResponse(_frontend("?oauth=success"), status_code=307)
    resp.set_cookie(
        "access_token", jwt_token,
        httponly=True, secure=_cookie_secure(), samesite="lax",
        max_age=get_settings().jwt_expire_minutes * 60, path="/",
    )
    return resp


@router.get("/me", response_model=UserOut)
async def me(user: User = Depends(get_current_user)) -> UserOut:
    """Текущий пользователь по сессии. Для соц-входа JWT лежит в httpOnly-cookie,
    которую JS прочитать не может, — фронт зовёт /me, чтобы узнать, кто вошёл, и
    восстановить сессию после reload (#129)."""
    return UserOut.model_validate(user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout() -> Response:
    """Гасим cookie-сессию соц-входа. Bearer-токен (localStorage) фронт снимает сам;
    здесь важно снести именно httpOnly-cookie, до которой JS не дотянется."""
    resp = Response(status_code=status.HTTP_204_NO_CONTENT)
    resp.delete_cookie("access_token", path="/")
    return resp
