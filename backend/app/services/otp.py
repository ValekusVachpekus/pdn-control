"""Бизнес-логика одноразовых кодов входа (passwordless OTP).

Код генерится криптослучайно (`secrets`), хранится только bcrypt-хэшем
(переиспользуем hash_password/verify_password). Здесь — чистая логика
(генерация, проверка пригодности кода), DB-операции живут в routers/auth.py.
Вынесено отдельно, чтобы покрыть юнит-тестами без БД.
"""
from __future__ import annotations

import secrets
from datetime import datetime, timezone

from ..config import get_settings
from ..models.email_code import EmailCode
from .auth import hash_password, verify_password

CODE_DIGITS = 6


def generate_code() -> str:
    """6-значный код; ведущие нули сохраняются (напр. 000123)."""
    return f"{secrets.randbelow(1_000_000):0{CODE_DIGITS}d}"


def hash_code(code: str) -> str:
    return hash_password(code)


def code_matches(code: str, code_hash: str) -> bool:
    return verify_password(code, code_hash)


def is_consumable(ec: EmailCode, now: datetime | None = None) -> bool:
    """Код можно проверять: не использован, попытки не исчерпаны, не протух."""
    now = now or datetime.now(timezone.utc)
    if ec.used:
        return False
    if (ec.attempts or 0) >= get_settings().otp_max_attempts:
        return False
    exp = ec.expires_at
    # Наивный datetime из БД трактуем как UTC, чтобы сравнение было корректным.
    if exp.tzinfo is None:
        exp = exp.replace(tzinfo=timezone.utc)
    return now < exp
