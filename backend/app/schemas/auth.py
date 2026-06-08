"""Pydantic-схемы для auth-эндпоинтов."""
from __future__ import annotations

import uuid

from pydantic import BaseModel, EmailStr, Field

from ..models.user import UserPlan


class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserOut(BaseModel):
    id: uuid.UUID
    email: EmailStr
    plan: UserPlan

    model_config = {"from_attributes": True}


class AuthOut(BaseModel):
    token: str
    user: UserOut
