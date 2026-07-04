"""ORM-модель одноразовых кодов входа (passwordless OTP).

Код в письме — plain (6 цифр), в БД — ТОЛЬКО bcrypt-хэш. У кода короткий TTL и
лимит попыток: пространство всего 10^6, без этих ограничений код подбирается
перебором. Старые живые коды email-а инвалидируются при запросе нового.
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from ..db import Base


class EmailCode(Base):
    __tablename__ = "email_codes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(320), nullable=False, index=True)
    # bcrypt-хэш кода, не plain.
    code_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    used: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
