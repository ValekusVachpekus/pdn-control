"""Юнит-тесты канонизации crawl-JSON для LLM-кэша (issue #31).

Чистые функции (_canonical_crawl/cache_key) Redis не трогают — контейнеры не
нужны. Проверяем, что волатильные поля (server_ip, cookie.expires, а также
существующие scan_id/таймстампы) не влияют на ключ, а содержательные — влияют,
и что исходный crawl не мутируется.
"""
from __future__ import annotations

import os

# Минимальный env, чтобы импорт app.config не падал при загрузке модуля.
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://pdn:pdn@127.0.0.1:5432/pdn")
os.environ.setdefault("JWT_SECRET", "test-test-test-test-test-test-test")
os.environ.setdefault("LLM_API_KEY", "")

from app.services.llm_cache import _canonical_crawl, cache_key  # noqa: E402


def _crawl(*, server_ip: str, expires: int, scan_id: str, started_at: str) -> dict:
    """Мок CrawlJSON статического сайта; различаются только волатильные поля."""
    return {
        "schema_version": "1.3",
        "meta": {
            "scan_id": scan_id,
            "started_at": started_at,
            "finished_at": started_at,
            "duration_ms": 1234,
            "server_ip": server_ip,
        },
        "summary": {"has_privacy_policy": True, "forms_total": 2},
        "pages": [
            {
                "url": "https://example.ru/",
                "cookies": [
                    {"name": "sid", "domain": "example.ru", "expires": expires},
                    {"name": "lang", "domain": "example.ru", "expires": expires + 999},
                ],
            }
        ],
    }


def test_volatile_fields_do_not_change_key():
    """Два скана статичного сайта с разными server_ip/expires/scan_id/временем
    дают ОДИН ключ."""
    a = _crawl(server_ip="10.0.0.1", expires=1_000_000, scan_id="s1", started_at="2026-06-14T10:00:00Z")
    b = _crawl(server_ip="93.184.216.34", expires=2_000_000, scan_id="s2", started_at="2026-06-14T18:30:00Z")
    assert cache_key(a) == cache_key(b)


def test_meaningful_change_changes_key():
    """Содержательное изменение (например, исчезла политика) меняет ключ."""
    a = _crawl(server_ip="10.0.0.1", expires=1_000_000, scan_id="s1", started_at="t")
    b = _crawl(server_ip="10.0.0.1", expires=1_000_000, scan_id="s1", started_at="t")
    b["summary"]["has_privacy_policy"] = False
    assert cache_key(a) != cache_key(b)


def test_canonical_strips_volatile_but_keeps_facts():
    """Канонический вид не содержит волатильных полей, но сохраняет факты."""
    canon = _canonical_crawl(_crawl(server_ip="10.0.0.1", expires=1_000_000, scan_id="s1", started_at="t"))
    assert "server_ip" not in canon["meta"]
    for vk in ("scan_id", "started_at", "finished_at", "duration_ms"):
        assert vk not in canon["meta"]
    for cookie in canon["pages"][0]["cookies"]:
        assert "expires" not in cookie
        assert cookie["name"]  # сам факт cookie остаётся
    assert canon["summary"]["forms_total"] == 2


def test_geo_fields_do_not_change_key():
    """Производные от server_ip geo-поля (страна/CDN/провайдер/ASN) не влияют на
    ключ: на CDN/round-robin сайте IP скачет между сканами, и без этого кэш
    промахивался → LLM перегонялся → недетерминизм (регрессия #75 × #31)."""
    a = _crawl(server_ip="10.0.0.1", expires=1, scan_id="s", started_at="t")
    b = _crawl(server_ip="10.0.0.1", expires=1, scan_id="s", started_at="t")
    a["meta"].update({"server_country": "RU", "server_is_cdn": False,
                      "hosting_provider": "VK LLC", "server_asn": 47541,
                      "server_country_confidence": "high", "server_country_source": "geoip"})
    b["meta"].update({"server_country": "US", "server_is_cdn": True,
                      "hosting_provider": "Cloudflare", "server_asn": 13335,
                      "server_country_confidence": "low", "server_country_source": "geoip"})
    assert cache_key(a) == cache_key(b)


def test_source_crawl_not_mutated():
    """_canonical_crawl работает на копии — исходный crawl не теряет поля."""
    src = _crawl(server_ip="10.0.0.1", expires=1_000_000, scan_id="s1", started_at="t")
    _canonical_crawl(src)
    assert src["meta"]["server_ip"] == "10.0.0.1"
    assert src["pages"][0]["cookies"][0]["expires"] == 1_000_000
