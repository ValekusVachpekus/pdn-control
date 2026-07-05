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


class RequestCodeIn(BaseModel):
    """Шаг 1 passwordless-входа: запрос кода на e-mail."""
    email: EmailStr


class VerifyCodeIn(BaseModel):
    """Шаг 2: проверка кода. `consent` обязателен только при ПЕРВОЙ регистрации
    (нового пользователя) — 152-ФЗ ст. 9; для существующего игнорируется."""
    email: EmailStr
    code: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")
    consent: bool = False


class ConfirmRegisterIn(BaseModel):
    """Шаг 2 регистрации по e-mail+password: подтверждение почты кодом.
    Пароль и согласие уже приняты на шаге 1 (лежат в pending-регистрации)."""
    email: EmailStr
    code: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")


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
