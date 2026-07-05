"""Юнит-тест pending-регистрации (Redis-стор) на фейковом клиенте."""
from __future__ import annotations

import os

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://pdn:pdn@127.0.0.1:5432/pdn")
os.environ.setdefault("JWT_SECRET", "test-test-test-test-test-test-test")
os.environ.setdefault("LLM_API_KEY", "")

from app.services import pending_registration as pr  # noqa: E402


class _FakeRedis:
    def __init__(self) -> None:
        self.store: dict[str, str] = {}

    def set(self, key: str, value: str, ex: int | None = None) -> bool:
        self.store[key] = value
        return True

    def get(self, key: str) -> str | None:
        return self.store.get(key)

    def delete(self, key: str) -> int:
        return 1 if self.store.pop(key, None) is not None else 0


def test_pending_roundtrip_and_single_use():
    c = _FakeRedis()
    data = {"password_hash": "$2b$hash", "consent": True}
    pr.save("User@Example.RU", data, client=c)
    # регистр e-mail не важен (ключ нормализуется)
    assert pr.pop("user@example.ru", client=c) == data
    # повторно — уже нет (одноразово)
    assert pr.pop("user@example.ru", client=c) is None
    # неизвестный e-mail
    assert pr.pop("nobody@example.ru", client=c) is None
