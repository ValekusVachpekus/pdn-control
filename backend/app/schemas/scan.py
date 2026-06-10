"""Pydantic-схемы для эндпоинтов проверки сайта и отчётов."""
from __future__ import annotations

import re
import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from ..models.scan import ScanStatus

# Валидация домена/URL. Это defense-in-depth: SQLAlchemy и так использует
# параметризованные запросы (нет SQL-инъекций), но мы режем мусор на входе.
_DOMAIN_RE = re.compile(
    r"^([a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}(?::\d{1,5})?$",
    re.IGNORECASE,
)


def normalize_domain(url: str) -> str:
    """example.com/ → example.com (без схемы и завершающего слэша)."""
    s = str(url).strip()
    s = re.sub(r"^https?://", "", s, flags=re.IGNORECASE)
    s = s.rstrip("/")
    return s.split("/", 1)[0].split("?", 1)[0].split("#", 1)[0]


class ScanCreateIn(BaseModel):
    url: str = Field(min_length=3, max_length=2048)

    @field_validator("url")
    @classmethod
    def _validate_url(cls, v: str) -> str:
        host = normalize_domain(v)
        if not _DOMAIN_RE.match(host):
            raise ValueError("invalid domain")
        return v.strip()


class ScanCreateOut(BaseModel):
    report_id: uuid.UUID


class ScanStatusOut(BaseModel):
    report_id: uuid.UUID
    status: ScanStatus
    error: str | None = None
    created_at: datetime
    finished_at: datetime | None = None
