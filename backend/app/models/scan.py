"""ORM-модель проверки сайта (scan) и связанного отчёта (Контракт №2 в JSONB)."""
from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from ..db import Base


class ScanStatus(str, enum.Enum):
    pending = "pending"     # задача поставлена в очередь
    running = "running"     # парсер/rule-engine работают
    done = "done"           # отчёт готов
    failed = "failed"       # упало с ошибкой


class Scan(Base):
    __tablename__ = "scans"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    domain: Mapped[str] = mapped_column(String(253), nullable=False, index=True)
    status: Mapped[ScanStatus] = mapped_column(
        Enum(ScanStatus, name="scan_status"), default=ScanStatus.pending, nullable=False
    )
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Разовая оплата за КОНКРЕТНЫЙ отчёт. False = free: фронту отдаём
    # урезанный JSON (без деталей нарушений, без инфраструктуры/AI/PDF).
    paid: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    # JSON Контракта №2 (то, что отдаём фронту/PDF-сервису)
    report_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
