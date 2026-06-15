"""Анти-SSRF на входе в /api/scans — defense-in-depth.

Основная защита от SSRF живёт в краулере (отдельный микросервис: сетевой
перехват каждого запроса/редиректа, см. crowler/pdn_parser/ssrf.py). Здесь —
дублирующий слой: отсекаем заведомо внутренние цели уже на постановке скана,
чтобы вернуть понятную 400, а не «провалившийся скан» спустя минуту.

Литеральные IP и localhost уже режет доменный регекс схемы (нужен TLD из букв);
этот модуль добавляет проверку РЕЗОЛВА — публичный по виду домен, указывающий
во внутренний адрес. Проверка best-effort и fail-OPEN: если DNS не ответил, не
блокируем (краулер всё равно перепроверит на сетевом уровне, fail-closed).
"""

from __future__ import annotations

import asyncio
import ipaddress
import socket

_BLOCKED_V4_NETS = (
    ipaddress.ip_network("100.64.0.0/10"),  # CGNAT (RFC 6598)
)
_BLOCKED_V6_NETS = (
    ipaddress.ip_network("64:ff9b::/96"),    # NAT64 (RFC 6052)
    ipaddress.ip_network("64:ff9b:1::/48"),
)

# Не ждём медленный DNS в request-хендлере дольше пары секунд.
_RESOLVE_TIMEOUT_SEC = 2.0


def _ip_is_safe(ip) -> bool:
    """True, если IP публичный маршрутизируемый (не внутренний/служебный)."""
    if isinstance(ip, ipaddress.IPv6Address):
        embedded = ip.ipv4_mapped or ip.sixtofour
        if embedded is not None:
            return _ip_is_safe(embedded)
        if any(ip in net for net in _BLOCKED_V6_NETS):
            return False
    elif any(ip in net for net in _BLOCKED_V4_NETS):
        return False
    return not (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_reserved
        or ip.is_multicast
        or ip.is_unspecified
    )


async def _resolve(host: str) -> list:
    loop = asyncio.get_running_loop()
    infos = await loop.getaddrinfo(host, None, type=socket.SOCK_STREAM)
    out: list = []
    for *_, sockaddr in infos:
        try:
            out.append(ipaddress.ip_address(sockaddr[0].split("%", 1)[0]))
        except ValueError:
            continue
    return out


async def internal_target_reason(host: str) -> str | None:
    """Причина блокировки, если host внутренний/резолвится во внутренний; иначе None.

    Fail-open: на ошибке/таймауте DNS возвращает None (не блокирует) — краулер
    остаётся последней линией обороны.
    """
    host = (host or "").strip().strip("[]")
    if not host:
        return None

    # Литеральный IP — проверяем без DNS.
    try:
        literal = ipaddress.ip_address(host.split("%", 1)[0])
    except ValueError:
        literal = None
    if literal is not None:
        return None if _ip_is_safe(literal) else f"адрес {host} внутренний/зарезервированный"

    try:
        ips = await asyncio.wait_for(_resolve(host), timeout=_RESOLVE_TIMEOUT_SEC)
    except (asyncio.TimeoutError, socket.gaierror, UnicodeError, OSError):
        return None  # fail-open
    for ip in ips:
        if not _ip_is_safe(ip):
            return f"хост {host} резолвится во внутренний адрес {ip}"
    return None
