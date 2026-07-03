"""Rate-limit отправки OTP: не чаще 1 кода/cooldown на e-mail и на IP.

Без этого request-code превращается в инструмент спам-рассылки и enumeration по
таймингу. Состояние — в Redis (sync-клиент, как в scan_progress). Если Redis
недоступен — fail-open (не блокируем легитимных пользователей), сбой логируем.
"""
from __future__ import annotations

import logging

import redis

from ..config import get_settings

log = logging.getLogger(__name__)

_redis: redis.Redis | None = None


def _client() -> redis.Redis:
    global _redis
    if _redis is None:
        _redis = redis.Redis.from_url(get_settings().redis_url, decode_responses=True)
    return _redis


def allow_otp_request(email: str, ip: str, *, client: redis.Redis | None = None) -> bool:
    """True — код слать можно (и ставим cooldown по email и IP).

    Отказ, если по этому e-mail ИЛИ IP кулдаун ещё активен. `client`
    инъектируется в тестах. Redis недоступен — пропускаем (fail-open).
    """
    s = get_settings()
    ttl = s.otp_resend_cooldown_sec
    ekey = f"otp:rl:email:{email.lower()}"
    ikey = f"otp:rl:ip:{ip}"
    try:
        c = client or _client()
        if c.exists(ekey) or c.exists(ikey):
            return False
        c.set(ekey, "1", ex=ttl)
        c.set(ikey, "1", ex=ttl)
        return True
    except redis.RedisError as exc:
        log.warning("rate-limit: Redis недоступен, пропускаю запрос (%s)", exc)
        return True
