"""Ожидающие подтверждения регистрации (e-mail + пароль) до ввода кода.

Пользователь создаётся ТОЛЬКО после подтверждения почты кодом. До этого bcrypt-
хэш пароля и факт согласия держим в Redis с TTL кода — не в БД, чтобы
неподтверждённый аккаунт не существовал (и не мог войти через /login). Redis
недоступен — вызов бросает исключение (fail-closed: без стора регистрацию не
начинаем).
"""
from __future__ import annotations

import json

import redis

from ..config import get_settings

_redis: redis.Redis | None = None


def _client() -> redis.Redis:
    global _redis
    if _redis is None:
        _redis = redis.Redis.from_url(get_settings().redis_url, decode_responses=True)
    return _redis


def _key(email: str) -> str:
    return f"reg:pending:{email.lower()}"


def save(email: str, data: dict, *, client: redis.Redis | None = None) -> None:
    """Кладёт данные ожидающей регистрации с TTL = otp_ttl_sec."""
    c = client or _client()
    c.set(_key(email), json.dumps(data), ex=get_settings().otp_ttl_sec)


def pop(email: str, *, client: redis.Redis | None = None) -> dict | None:
    """Возвращает данные и УДАЛЯЕТ их (одноразово). None — если нет/протух."""
    c = client or _client()
    raw = c.get(_key(email))
    if raw is None:
        return None
    c.delete(_key(email))
    return json.loads(raw)
