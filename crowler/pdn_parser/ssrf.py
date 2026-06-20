"""Анти-SSRF для краулера.

Проблема: ``fetch_page`` ходит по URL, полученному от пользователя, через
Playwright. Без сетевой проверки краулер можно увести на внутренние ресурсы
(loopback, private-сети, link-local, облачная метадата ``169.254.169.254``) —
напрямую, через 30x-редирект на внутренний адрес или через DNS rebinding.

Подход — проверка на СЕТЕВОМ уровне, fail-closed:

* каждый запрос браузера (исходный, **каждый редирект** и сабресурсы)
  перехватывается через ``context.route`` и блокируется, если хост резолвится
  в небезопасный IP — а не только исходный URL;
* резолвятся ВСЕ A/AAAA-записи (а не первый IPv4), учитываются IPv6 и
  IPv4-mapped/6to4-обёртки, обфусцированные литералы (``0x7f.. ``, целочисленная
  форma) ловятся, т.к. их резолвит ОС и мы валидируем фактический IP;
* резолв асинхронный (``loop.getaddrinfo``) — event loop НЕ блокируется;
* после навигации фактический IP origin'а (``Response.server_addr``) валидируется
  ПОВТОРНО — это ловит DNS rebinding, когда на момент проверки хост отдавал
  безопасный IP, а на момент коннекта браузер получил внутренний.

Модуль самодостаточен и не зависит от Playwright на уровне импорта — ``install``
лишь регистрирует обработчик на переданном context'е.
"""

from __future__ import annotations

import asyncio
import ipaddress
import socket
from dataclasses import dataclass
from typing import Awaitable, Callable
from urllib.parse import urlparse

_ALLOWED_SCHEMES = {"http", "https"}

# Доп. диапазоны, которые встроенные флаги ipaddress не помечают как
# приватные/зарезервированные (зависит от версии Python), но через которые можно
# достучаться до внутренней сети.
# CGNAT 100.64.0.0/10 (RFC 6598) — shared address space провайдеров/облаков.
_BLOCKED_V4_NETS = (
    ipaddress.ip_network("100.64.0.0/10"),
)
# NAT64 (RFC 6052) транслирует встроенный IPv4 — резолвер ОС может вернуть такой
# адрес для внутреннего хоста.
_BLOCKED_V6_NETS = (
    ipaddress.ip_network("64:ff9b::/96"),
    ipaddress.ip_network("64:ff9b:1::/48"),
)

# Тип резолвера вынесен ради тестируемости: тесты подменяют его фейком и не
# ходят в реальный DNS.
Resolver = Callable[[str], Awaitable[list]]


@dataclass(frozen=True)
class Verdict:
    allowed: bool
    reason: str = ""


def _ip_is_safe(ip) -> bool:
    """True, если IP — публичный маршрутизируемый адрес (не внутренний/служебный).

    Покрывает IPv4 и IPv6: loopback, private (включая CGNAT 100.64/10),
    link-local (в т.ч. метадату 169.254.169.254), ULA, reserved, multicast,
    unspecified. IPv4, завёрнутый в IPv6 (``::ffff:127.0.0.1`` / 6to4), и NAT64
    разворачиваются и проверяются по встроенному адресу.
    """
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


def ip_str_is_safe(ip_str: str | None) -> bool:
    """Безопасен ли строковый IP. Непарсящийся/пустой → считаем безопасным.

    Используется для post-навигационной проверки фактического IP из
    ``Response.server_addr`` (best-effort: если браузер IP не отдал, блокировать
    не за что — сетевой перехват уже отработал на каждом запросе)."""
    if not ip_str:
        return True
    try:
        return _ip_is_safe(ipaddress.ip_address(ip_str.split("%", 1)[0]))
    except ValueError:
        return True


def _parse_ip_literal(host: str):
    """IP-литерал из host'а урла (или None, если это доменное имя)."""
    h = host.strip()
    if h.startswith("[") and h.endswith("]"):  # [::1] → ::1 (на случай, если скобки дошли)
        h = h[1:-1]
    h = h.split("%", 1)[0]  # отбросить zone-id (fe80::1%eth0)
    try:
        return ipaddress.ip_address(h)
    except ValueError:
        return None


async def _default_resolve(host: str) -> list:
    """Все IP хоста через неблокирующий getaddrinfo (A + AAAA)."""
    loop = asyncio.get_running_loop()
    infos = await loop.getaddrinfo(host, None, type=socket.SOCK_STREAM)
    out: list = []
    seen: set[str] = set()
    for *_, sockaddr in infos:
        ip_str = sockaddr[0].split("%", 1)[0]
        if ip_str in seen:
            continue
        seen.add(ip_str)
        try:
            out.append(ipaddress.ip_address(ip_str))
        except ValueError:
            continue
    return out


class SSRFGuard:
    """Проверяет URL'ы и режет запросы во внутренние/служебные адреса.

    Один экземпляр на одну страницу/контекст: держит кэш вердиктов по хосту,
    чтобы не резолвить один и тот же хост на каждый сабресурс (десятки запросов
    с одной страницы). Кэш живёт в пределах загрузки страницы — окно для
    rebinding ограничено и закрывается повторной проверкой ``server_addr``.
    """

    def __init__(self, resolver: Resolver | None = None) -> None:
        self._resolve = resolver or _default_resolve
        self._cache: dict[str, Verdict] = {}

    async def check_url(self, url: str) -> Verdict:
        try:
            parsed = urlparse(url)
        except ValueError:
            return Verdict(False, "некорректный URL")
        scheme = (parsed.scheme or "").lower()
        if scheme not in _ALLOWED_SCHEMES:
            shown = scheme or "(пусто)"
            return Verdict(False, f"схема '{shown}' запрещена (разрешены только http/https)")
        host = parsed.hostname
        if not host:
            return Verdict(False, "URL без хоста")

        key = host.lower()
        cached = self._cache.get(key)
        if cached is not None:
            return cached
        verdict = await self._check_host(host)
        self._cache[key] = verdict
        return verdict

    async def _check_host(self, host: str) -> Verdict:
        literal = _parse_ip_literal(host)
        if literal is not None:
            if _ip_is_safe(literal):
                return Verdict(True)
            return Verdict(False, f"адрес {host} — внутренний/зарезервированный")

        try:
            ips = await self._resolve(host)
        except (socket.gaierror, UnicodeError, OSError) as exc:
            # Не резолвится — fail-closed: лучше не ходить, чем рискнуть.
            return Verdict(False, f"хост {host} не резолвится ({exc})")
        if not ips:
            return Verdict(False, f"хост {host} не резолвится")
        for ip in ips:
            if not _ip_is_safe(ip):
                return Verdict(False, f"хост {host} резолвится во внутренний адрес {ip}")
        return Verdict(True)

    async def install(self, context, on_block: Callable[[str, str, bool], None] | None = None) -> None:
        """Повесить сетевой перехват на Playwright BrowserContext.

        Каждый запрос (включая редиректы и сабресурсы) проверяется; небезопасные
        — абортятся с ERR_BLOCKED_BY_CLIENT. ``on_block(url, reason, is_main_nav)``
        вызывается на каждый заблокированный запрос; ``is_main_nav`` отличает блок
        навигации ГЛАВНОГО документа (краулер реально увели на внутренний адрес)
        от блока стороннего сабресурса (аналитика/пиксель — не должен валить скан).
        """

        async def handler(route) -> None:
            req = route.request
            url = req.url
            verdict = await self.check_url(url)
            try:
                if verdict.allowed:
                    await route.continue_()
                else:
                    if on_block is not None:
                        on_block(url, verdict.reason, _is_main_navigation(req))
                    await route.abort("blockedbyclient")
            except Exception:
                # Контекст мог закрыться / запрос уже обработан — глушим, чтобы
                # не валить обработчик (иначе Playwright считает route незакрытым).
                pass

        await context.route("**/*", handler)


def _is_main_navigation(request) -> bool:
    """True, если запрос — навигация ГЛАВНОГО документа, а не сабресурс/iframe.

    Блок такого запроса означает, что краулер увели на внутренний адрес — это
    SSRF, на нём короткозамыкаемся. Блок сабресурса (сторонний трекер/виджет,
    резолвящийся во flagged-адрес) не должен маскировать таймаут под SSRF и
    отменять мягкий ретрай главного документа.
    """
    try:
        if not request.is_navigation_request():
            return False
        return request.frame.parent_frame is None
    except Exception:
        return False
