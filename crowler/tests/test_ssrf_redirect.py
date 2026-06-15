"""Тесты guarded-GET для robots.txt/sitemap.xml (issue #37).

Эти запросы идут через httpx мимо Playwright-перехвата, поэтому SSRF-проверку
делает _guarded_get. Главный кейс — публичный URL/сокращатель, 30x-редиректящий
на внутренний адрес: исходный хоп проходит, редирект-хоп режется.

httpx не ходит в сеть: подменяем транспорт MockTransport. DNS не трогаем —
используем литеральные IP (check_url проверяет литералы без резолва).
"""
import asyncio

import httpx
import pytest

from pdn_parser import crawler


def _patch_transport(monkeypatch, handler):
    real_client = httpx.AsyncClient

    def fake_client(*args, **kwargs):
        kwargs.pop("follow_redirects", None)
        return real_client(transport=httpx.MockTransport(handler), follow_redirects=False)

    monkeypatch.setattr(crawler.httpx, "AsyncClient", fake_client)


def test_guarded_get_blocks_redirect_to_internal(monkeypatch):
    """Публичный литерал -> 302 на cloud-метадату. Редирект-хоп должен резаться."""
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.host == "93.184.216.34":
            return httpx.Response(302, headers={"location": "http://169.254.169.254/latest/"})
        return httpx.Response(200, text="should-not-reach")

    _patch_transport(monkeypatch, handler)
    with pytest.raises(crawler._SSRFBlocked):
        asyncio.run(crawler._guarded_get("http://93.184.216.34/robots.txt"))


def test_guarded_get_allows_public_redirect(monkeypatch):
    """Редирект на другой публичный адрес — проходит, тело возвращается."""
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.host == "93.184.216.34":
            return httpx.Response(301, headers={"location": "http://8.8.8.8/robots.txt"})
        return httpx.Response(200, text="User-agent: *")

    _patch_transport(monkeypatch, handler)
    resp = asyncio.run(crawler._guarded_get("http://93.184.216.34/robots.txt"))
    assert resp.status_code == 200 and "User-agent" in resp.text


def test_guarded_get_blocks_internal_first_hop(monkeypatch):
    """Сам исходный URL — внутренний литерал: блок без единого запроса."""
    def handler(request: httpx.Request) -> httpx.Response:
        raise AssertionError("запрос не должен был уйти")

    _patch_transport(monkeypatch, handler)
    with pytest.raises(crawler._SSRFBlocked):
        asyncio.run(crawler._guarded_get("http://127.0.0.1/sitemap.xml"))


def test_guarded_get_redirect_loop_capped(monkeypatch):
    """Бесконечный редирект на публичные адреса не вешает — упираемся в лимит."""
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(302, headers={"location": "http://8.8.8.8/next"})

    _patch_transport(monkeypatch, handler)
    with pytest.raises(crawler._SSRFBlocked):
        asyncio.run(crawler._guarded_get("http://8.8.8.8/start"))
