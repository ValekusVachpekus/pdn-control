"""Регистрация и логин по email/паролю."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_session
from ..models.user import User, UserPlan
from ..schemas.auth import AuthOut, LoginIn, RegisterIn, UserOut
from ..services.auth import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=AuthOut, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterIn, session: AsyncSession = Depends(get_session)) -> AuthOut:
    existing = await session.scalar(select(User).where(User.email == body.email.lower()))
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="email already registered")

    user = User(
        email=body.email.lower(),
        password_hash=hash_password(body.password),
        plan=UserPlan.free,
    )
    session.add(user)
    await session.flush()  # чтобы получить user.id до коммита

    token = create_access_token(user.id)
    return AuthOut(token=token, user=UserOut.model_validate(user))


@router.post("/login", response_model=AuthOut)
async def login(body: LoginIn, session: AsyncSession = Depends(get_session)) -> AuthOut:
    user = await session.scalar(select(User).where(User.email == body.email.lower()))
    # Одинаковая 401 на «нет такого юзера» и «не тот пароль» — не утекает наружу,
    # есть ли аккаунт с таким email.
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")

    token = create_access_token(user.id)
    return AuthOut(token=token, user=UserOut.model_validate(user))
