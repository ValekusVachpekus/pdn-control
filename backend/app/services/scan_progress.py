"""Прогресс сканирования в Redis — реальные фазы, без фейковой анимации.

Краулер — отдельный микросервис, который возвращает результат разом, поэтому
per-page прогресс невозможен без его доработки. Но фазы конвейера РЕАЛЬНЫ:

    queued     — задача поставлена, воркер ещё не взял
    crawling   — воркер вызывает парсер, идёт обход страниц
    analyzing  — парсер отдал факты, идёт LLM-анализ (тут уже знаем реальные
                 числа: страниц обойдено, форм, трекеров)
    building   — LLM ответил, собираем итоговый Контракт №2
    done       — отчёт готов
    failed     — упало (см. поле error)

Фронт опрашивает GET /api/scans/{id}/progress и показывает текущую фазу с
реальными счётчиками. TTL короткий — данные нужны только пока скан идёт.
"""
from __future__ import annotations

import json
import logging
import time
from typing import Any

import redis

from ..config import get_settings

log = logging.getLogger(__name__)

PROGRESS_TTL_SEC = 600  # 10 минут — больше длиться скан не должен
_KEY_PREFIX = "scan_progress:"

# Известные фазы (для фронта — порядок и подписи). Порядок задаёт прогресс-бар.
PHASES = ("queued", "crawling", "analyzing", "building", "done", "failed")

_redis: redis.Redis | None = None


def _client() -> redis.Redis:
    global _redis
    if _redis is None:
        s = get_settings()
        _redis = redis.Redis.from_url(
            s.redis_url, decode_responses=True,
            socket_timeout=2, socket_connect_timeout=2,
        )
    return _redis


def _key(scan_id: str) -> str:
    return f"{_KEY_PREFIX}{scan_id}"


def set_phase(scan_id: str, phase: str, **extra: Any) -> None:
    """Записать текущую фазу + произвольные счётчики. Ошибки Redis глушим —
    прогресс это вспомогательная информация, она не должна ронять скан."""
    payload = {"phase": phase, "ts": int(time.time()), **extra}
    try:
        _client().set(_key(scan_id), json.dumps(payload, ensure_ascii=False),
                      ex=PROGRESS_TTL_SEC)
    except redis.RedisError as exc:
        log.warning("scan_progress set failed: %s", exc)


def get(scan_id: str) -> dict[str, Any] | None:
    """Текущий прогресс или None, если ничего не записано (TTL истёк / нет ключа)."""
    try:
        raw = _client().get(_key(scan_id))
    except redis.RedisError as exc:
        log.warning("scan_progress get failed: %s", exc)
        return None
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def clear(scan_id: str) -> None:
    try:
        _client().delete(_key(scan_id))
    except redis.RedisError:
        pass
