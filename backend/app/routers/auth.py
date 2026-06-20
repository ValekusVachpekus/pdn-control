"""Регистрация / логин по email+password + OAuth-заглушки (Яндекс/ВК).

Реальный OAuth-flow (редирект → провайдер → callback → JWT) — отдельная задача:
здесь возвращаем 501 c понятным сообщением, чтобы это нельзя было перепутать
с рабочим эндпоинтом. Конструкция сохраняет контракт с фронтом — когда OAuth
будет готов, поменяем только тело функции.
"""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_session
from ..models.user import User
from ..plans import POLICY_VERSION
from ..schemas.auth import AuthOut, LoginIn, OAuthIn, RegisterIn, UserOut
from ..services.auth import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])

_OAUTH_PROVIDERS = {"yandex", "vk"}


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
