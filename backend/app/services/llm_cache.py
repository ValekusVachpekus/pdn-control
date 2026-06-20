"""Кеш JSON-ответов LLM в Redis.

Ключ — sha256 от «канонического» crawl-JSON (то есть от тех его полей, которые
влияют на анализ; вырезаем нестабильные timestamps/duration/scan_id, иначе один
и тот же сайт всегда давал бы cache-miss).

TTL — 7 дней: за неделю крупных изменений сайта обычно не происходит, дешевле
перепроверить раз в неделю чем гонять LLM на каждый платный скан.
"""
from __future__ import annotations

import hashlib
import json
import logging
from typing import Any

import redis

from ..config import get_settings

log = logging.getLogger(__name__)

CACHE_VERSION = "v1"
CACHE_TTL_SEC = 7 * 24 * 3600  # 7 дней

_KEY_PREFIX = f"llm_cache:{CACHE_VERSION}:"

# Поля Контракта №1, которые НЕ влияют на анализ (меняются от скана к скану).
# Их вычищаем перед хешированием.
_VOLATILE_META_KEYS = {
    "scan_id", "started_at", "finished_at", "duration_ms",
    # server_ip: IP origin'а; на CDN/round-robin DNS меняется между сканами,
    # хотя сам сайт неизменен → cache-miss. Остаётся в исходном CrawlJSON.
    "server_ip",
}

# Волатильные поля cookie: значение-факт, но нестабильное между сканами.
_VOLATILE_COOKIE_KEYS = {
    # expires: абсолютный Unix-таймстамп (now + max-age) → отличается просто
    # из-за разного времени запуска скана.
    "expires",
}


_redis: redis.Redis | None = None


def _client() -> redis.Redis:
    """Лениво создаём подключение — один процесс воркера переиспользует его."""
    global _redis
    if _redis is None:
        s = get_settings()
        _redis = redis.Redis.from_url(s.redis_url, decode_responses=True,
                                       socket_timeout=2, socket_connect_timeout=2)
    return _redis


def _canonical_crawl(crawl: dict[str, Any]) -> dict[str, Any]:
    """Вырезает нестабильные поля. Хеш канонического вида одинаков для одного
    и того же сайта, даже если время скана, id и server_ip разные.

    Работает на deep-copy (json round-trip) — исходный crawl не мутируется,
    поля server_ip/expires остаются в выдаче и отчёте."""
    canon = json.loads(json.dumps(crawl, ensure_ascii=False, sort_keys=True))
    meta = canon.get("meta")
    if isinstance(meta, dict):
        for k in _VOLATILE_META_KEYS:
            meta.pop(k, None)
    # Рекурсивно по вложенным cookies: pages[*].cookies[*].expires.
    for page in canon.get("pages", []) or []:
        if not isinstance(page, dict):
            continue
        for cookie in page.get("cookies", []) or []:
            if isinstance(cookie, dict):
                for k in _VOLATILE_COOKIE_KEYS:
                    cookie.pop(k, None)
    return canon


def cache_key(crawl: dict[str, Any]) -> str:
    canon = _canonical_crawl(crawl)
    blob = json.dumps(canon, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return _KEY_PREFIX + hashlib.sha256(blob).hexdigest()


def get(crawl: dict[str, Any]) -> dict[str, Any] | None:
    """Вернёт распарсенный LLM-output либо None при miss / ошибке Redis."""
    try:
        raw = _client().get(cache_key(crawl))
    except redis.RedisError as exc:
        log.warning("LLM cache get failed: %s", exc)
        return None
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        log.warning("LLM cache: stored value is not valid JSON, ignoring")
        return None


def set_(crawl: dict[str, Any], llm_output: dict[str, Any]) -> None:
    """Кладём LLM-output в кеш. Ошибки Redis глотаем — это just-cache, не блокер."""
    try:
        _client().set(
            cache_key(crawl),
            json.dumps(llm_output, ensure_ascii=False),
            ex=CACHE_TTL_SEC,
        )
    except redis.RedisError as exc:
        log.warning("LLM cache set failed: %s", exc)
