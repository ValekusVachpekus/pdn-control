"""Хранилище OAuth-state (CSRF) между /start и /callback.

В state кладём провайдера, флаг согласия и PKCE code_verifier — их нужно
пронести через редиректы, но НЕ отдавать клиенту. Redis с TTL: state
одноразовый (удаляется при извлечении). Redis недоступен — вызов бросает
исключение (fail-closed: без CSRF-стейта OAuth начинать нельзя).
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


def _key(state: str) -> str:
    return f"oauth:state:{state}"


def save_state(state: str, payload: dict, *, client: redis.Redis | None = None) -> None:
    c = client or _client()
    c.set(_key(state), json.dumps(payload), ex=get_settings().oauth_state_ttl_sec)


def pop_state(state: str, *, client: redis.Redis | None = None) -> dict | None:
    """Возвращает payload и УДАЛЯЕТ state (одноразовый). None — если нет/протух."""
    c = client or _client()
    raw = c.get(_key(state))
    if raw is None:
        return None
    c.delete(_key(state))
    return json.loads(raw)
