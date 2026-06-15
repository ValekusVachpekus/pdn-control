"""Тесты анти-SSRF гарда краулера (issue #37).

Сетевой DNS не трогаем: резолвер инъектируется фейком, асинхронные функции
гоняем через asyncio.run — так тесты быстрые и детерминированные, без браузера.
"""
import asyncio
import ipaddress

import pytest

from pdn_parser.ssrf import SSRFGuard, ip_str_is_safe


def ip(s):
    return ipaddress.ip_address(s)


def fake_resolver(mapping):
    """Возвращает async-резолвер, отдающий заранее заданные IP по хосту.

    mapping[host] = ["1.2.3.4", ...]  или  Exception для имитации сбоя DNS.
    """
    async def _resolve(host):
        val = mapping[host]
        if isinstance(val, Exception):
            raise val
        return [ip(x) for x in val]
    return _resolve


def check(url, mapping):
    guard = SSRFGuard(resolver=fake_resolver(mapping))
    return asyncio.run(guard.check_url(url))


# --- классификация IP -------------------------------------------------------

SAFE_IPS = ["8.8.8.8", "1.1.1.1", "93.184.216.34",
            "2606:4700:4700::1111", "::ffff:8.8.8.8"]

BLOCKED_IPS = [
    "127.0.0.1", "127.255.255.254",      # loopback
    "::1",                                # loopback v6
    "169.254.169.254",                   # облачная метадата (link-local)
    "10.0.0.5", "172.16.0.1", "192.168.1.1",  # private
    "100.64.0.1",                        # CGNAT
    "0.0.0.0",                           # unspecified
    "::",                                # unspecified v6
    "240.0.0.1",                         # reserved
    "224.0.0.1", "ff02::1",              # multicast
    "fe80::1",                           # link-local v6
    "fc00::1", "fd00::1",                # ULA v6
    "::ffff:127.0.0.1",                  # IPv4-mapped loopback
    "::ffff:169.254.169.254",            # IPv4-mapped метадата
    "64:ff9b::7f00:1",                   # NAT64 -> 127.0.0.1
]


@pytest.mark.parametrize("addr", SAFE_IPS)
def test_public_ip_allowed(addr):
    assert ip_str_is_safe(addr) is True


@pytest.mark.parametrize("addr", BLOCKED_IPS)
def test_internal_ip_blocked(addr):
    assert ip_str_is_safe(addr) is False


def test_ip_str_safe_on_empty_or_garbage():
    # Нет данных / непарсится — не за что блокировать (post-check best-effort).
    assert ip_str_is_safe(None) is True
    assert ip_str_is_safe("") is True
    assert ip_str_is_safe("not-an-ip") is True


# --- check_url: схемы и хост ------------------------------------------------

@pytest.mark.parametrize("url", [
    "ftp://example.com/", "file:///etc/passwd",
    "javascript:alert(1)", "gopher://example.com/",
])
def test_non_http_scheme_rejected(url):
    v = check(url, {})
    assert not v.allowed and "схема" in v.reason


def test_missing_host_rejected():
    v = check("http:///path", {})
    assert not v.allowed


# --- литеральные адреса (без DNS) ------------------------------------------

def test_literal_internal_ip_rejected_without_dns():
    # Резолвер пустой: если бы гард полез в DNS — был бы KeyError. Значит литерал
    # проверяется напрямую.
    v = check("http://169.254.169.254/latest/meta-data/", {})
    assert not v.allowed and "169.254.169.254" in v.reason


def test_literal_ipv6_loopback_rejected():
    v = check("http://[::1]:8080/", {})
    assert not v.allowed


def test_literal_public_ip_allowed():
    assert check("https://8.8.8.8/", {}).allowed


# --- резолв доменов ---------------------------------------------------------

def test_public_domain_allowed():
    assert check("https://example.com/", {"example.com": ["93.184.216.34"]}).allowed


def test_domain_resolving_to_internal_rejected():
    v = check("http://evil.example/", {"evil.example": ["127.0.0.1"]})
    assert not v.allowed and "внутренний" in v.reason


def test_any_internal_among_multiple_records_blocks():
    # Множественные A-записи: один публичный + один внутренний -> блок.
    v = check("http://multi.example/", {"multi.example": ["93.184.216.34", "10.0.0.1"]})
    assert not v.allowed


def test_ipv6_only_internal_rejected():
    # AAAA во внутренний адрес (первый IPv4 проигнорировал бы такую дыру).
    v = check("http://v6.example/", {"v6.example": ["fc00::1"]})
    assert not v.allowed


def test_dns_failure_fails_closed():
    import socket
    v = check("http://nx.example/", {"nx.example": socket.gaierror("no such host")})
    assert not v.allowed and "не резолвится" in v.reason


def test_verdict_is_cached_per_host():
    calls = {"n": 0}

    async def counting_resolver(host):
        calls["n"] += 1
        return [ip("93.184.216.34")]

    guard = SSRFGuard(resolver=counting_resolver)

    async def run():
        await guard.check_url("https://example.com/a")
        await guard.check_url("https://example.com/b")  # тот же хост
        await guard.check_url("https://EXAMPLE.com/c")  # регистр не важен
    asyncio.run(run())
    assert calls["n"] == 1


# --- редирект на внутренний адрес (сетевой уровень) ------------------------

def test_redirect_chain_blocks_internal_hop():
    """Публичный URL -> 30x на внутренний. Гард проверяет КАЖДЫЙ запрос, поэтому
    исходный проходит, а редирект-хоп режется — обход исходной проверки закрыт."""
    mapping = {"public.example": ["93.184.216.34"], "internal.example": ["169.254.169.254"]}
    guard = SSRFGuard(resolver=fake_resolver(mapping))

    async def run():
        first = await guard.check_url("http://public.example/")        # исходный запрос
        second = await guard.check_url("http://internal.example/")     # редирект-хоп
        return first, second

    first, second = asyncio.run(run())
    assert first.allowed
    assert not second.allowed and "169.254.169.254" in second.reason


# --- install(): блок навигации главного документа vs сабресурса --------------

class _FakeFrame:
    def __init__(self, parent):
        self.parent_frame = parent


class _FakeRequest:
    def __init__(self, url, is_nav, parent_frame=None):
        self.url = url
        self._is_nav = is_nav
        self.frame = _FakeFrame(parent_frame)

    def is_navigation_request(self):
        return self._is_nav


class _FakeRoute:
    def __init__(self, request):
        self.request = request
        self.action = None

    async def continue_(self):
        self.action = "continue"

    async def abort(self, *_):
        self.action = "abort"


class _FakeContext:
    def __init__(self):
        self.handler = None

    async def route(self, pattern, handler):
        self.handler = handler


def test_install_distinguishes_main_nav_from_subresource():
    """Блок главной навигации помечается is_main_nav=True, сабресурса/iframe — False.

    Это и есть фикс ложного провала скана: таймаут goto при заблокированном
    стороннем пикселе НЕ должен короткозамыкаться на SSRF и отменять ретрай."""
    mapping = {"evil.example": ["169.254.169.254"], "pub.example": ["8.8.8.8"]}
    guard = SSRFGuard(resolver=fake_resolver(mapping))
    ctx = _FakeContext()
    events = []

    async def run():
        await guard.install(ctx, on_block=lambda u, r, nav: events.append((u, nav)))
        main_nav = _FakeRoute(_FakeRequest("http://evil.example/", True, parent_frame=None))
        subresource = _FakeRoute(_FakeRequest("http://evil.example/px.gif", False))
        iframe_nav = _FakeRoute(_FakeRequest("http://evil.example/f", True, parent_frame=object()))
        allowed = _FakeRoute(_FakeRequest("http://pub.example/", True, parent_frame=None))
        for r in (main_nav, subresource, iframe_nav, allowed):
            await ctx.handler(r)
        return main_nav, subresource, iframe_nav, allowed

    main_nav, subresource, iframe_nav, allowed = asyncio.run(run())
    assert main_nav.action == "abort" and subresource.action == "abort"
    assert iframe_nav.action == "abort" and allowed.action == "continue"
    # навигацией главного документа считается только первый блок
    assert ("http://evil.example/", True) in events
    assert ("http://evil.example/px.gif", False) in events
    assert ("http://evil.example/f", False) in events
    assert all(u != "http://pub.example/" for u, _ in events)
