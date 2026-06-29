"""Юнит-тесты passwordless OTP (генерация/хэш/пригодность кода + rate-limit).

Чистая логика — БД/Redis не нужны: EmailCode конструируем в памяти, rate-limit
тестируем на фейковом Redis-клиенте. Покрываем критичные критерии #55:
happy-path verify, протухший/израсходованный/исчерпанный код, хранение только
хэша, работа rate-limit.
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://pdn:pdn@127.0.0.1:5432/pdn")
os.environ.setdefault("JWT_SECRET", "test-test-test-test-test-test-test")
os.environ.setdefault("LLM_API_KEY", "")

from app.models.email_code import EmailCode  # noqa: E402
from app.services import otp, rate_limit  # noqa: E402


def _code(**kw) -> EmailCode:
    base = dict(
        email="a@b.ru", code_hash="x",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
        attempts=0, used=False,
    )
    base.update(kw)
    return EmailCode(**base)


def test_generate_code_is_six_digits():
    for _ in range(300):
        c = otp.generate_code()
        assert len(c) == 6 and c.isdigit()


def test_code_stored_as_hash_not_plain():
    code = otp.generate_code()
    h = otp.hash_code(code)
    assert h != code
    assert otp.code_matches(code, h) is True
    wrong = "000000" if code != "000000" else "111111"
    assert otp.code_matches(wrong, h) is False


def test_fresh_code_consumable():
    assert otp.is_consumable(_code()) is True


def test_expired_code_not_consumable():
    ec = _code(expires_at=datetime.now(timezone.utc) - timedelta(seconds=1))
    assert otp.is_consumable(ec) is False


def test_used_code_not_consumable():
    assert otp.is_consumable(_code(used=True)) is False


def test_attempts_exhausted_not_consumable():
    ec = _code(attempts=otp.get_settings().otp_max_attempts)
    assert otp.is_consumable(ec) is False


def test_naive_expiry_treated_as_utc():
    """expires_at без tzinfo (как может прийти из БД) не должен ронять сравнение."""
    naive = (datetime.now(timezone.utc) + timedelta(minutes=5)).replace(tzinfo=None)
    ec = _code(expires_at=naive)
    assert otp.is_consumable(ec) is True


class _FakeRedis:
    """Мини-Redis для теста rate-limit: exists/set без TTL-эмуляции."""
    def __init__(self) -> None:
        self.store: dict[str, str] = {}

    def exists(self, key: str) -> int:
        return 1 if key in self.store else 0

    def set(self, key: str, value: str, ex: int | None = None) -> bool:
        self.store[key] = value
        return True


def test_rate_limit_blocks_repeat_by_email_and_ip():
    c = _FakeRedis()
    assert rate_limit.allow_otp_request("a@b.ru", "1.1.1.1", client=c) is True
    # тот же e-mail — отказ
    assert rate_limit.allow_otp_request("a@b.ru", "9.9.9.9", client=c) is False
    # тот же IP, другой e-mail — отказ
    assert rate_limit.allow_otp_request("c@d.ru", "1.1.1.1", client=c) is False
    # другой e-mail и IP — можно
    assert rate_limit.allow_otp_request("e@f.ru", "2.2.2.2", client=c) is True
