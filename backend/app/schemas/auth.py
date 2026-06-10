"""Pydantic-схемы для auth-эндпоинтов."""
from __future__ import annotations

import uuid

from pydantic import BaseModel, EmailStr, Field


class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    # 152-ФЗ ст. 9: согласие — обязательное условие регистрации.
    consent: bool = Field(
        ...,
        description="Согласие на обработку ПДн. Должно быть true, иначе 400.",
    )


class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class OAuthIn(BaseModel):
    """Тело при входе через провайдера. `consent` обязателен только при ПЕРВОЙ
    регистрации (для существующего пользователя бэкенд может игнорировать)."""
    consent: bool = False


class UserOut(BaseModel):
    id: uuid.UUID
    email: EmailStr
    oauth_provider: str | None = None

    model_config = {"from_attributes": True}


class AuthOut(BaseModel):
    token: str
    user: UserOut
