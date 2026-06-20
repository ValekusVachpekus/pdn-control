"""ORM-модель пользователя.

Подписок нет — оплата теперь привязана к конкретному отчёту (см. Scan.paid).
Здесь храним только идентификацию + доказательство согласия на обработку ПДн
(152-ФЗ ст. 9 требует, чтобы оператор мог подтвердить факт согласия).
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from ..db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False, index=True)
    # nullable: OAuth-юзеры могут не иметь локального пароля
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # "yandex" | "vk" | None — если зарегистрирован через провайдера
    oauth_provider: Mapped[str | None] = mapped_column(String(16), nullable=True)
    # 152-ФЗ ст. 9: момент фиксации согласия + версия политики, на которую согласился
    consent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    consent_policy_version: Mapped[str | None] = mapped_column(String(16), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    is_verified: Mapped[bool] = mapped_column(default=False, nullable=False)
    verification_code: Mapped[str | None] = mapped_column(String(6), nullable=True)
