"""Юнит-тесты детерминированного гео (_analyze_geo без LLM).

Гео теперь берётся из offline-GeoIP парсера (meta.server_country/...), а не
угадывается моделью. Проверяем статус локализации, CDN-guard (не штрафуем
вслепую на 6 млн) и воспроизводимость.
"""
from __future__ import annotations

import os

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://pdn:pdn@127.0.0.1:5432/pdn")
os.environ.setdefault("JWT_SECRET", "test-test-test-test-test-test-test")
os.environ.setdefault("LLM_API_KEY", "")

from app.services import llm_analyzer as la  # noqa: E402


def _pii_crawl(country="US", ip="8.8.8.8", is_cdn=False, cross=False) -> dict:
    """Сайт, обрабатывающий ПДн (форма с email без согласия)."""
    return {
        "meta": {
            "server_ip": ip, "server_country": country,
            "server_is_cdn": is_cdn, "hosting_provider": "Acme Cloud",
        },
        "summary": {
            "has_privacy_policy": False, "forms_total": 1, "forms_collecting_pii": 1,
            "forms_pii_without_consent": 1, "has_cookie_banner": False,
            "third_party_domain_count": 0, "trackers": [],
            "has_cross_border_transfer": cross,
        },
        "site_identity": {"inn": [], "ogrn": [], "legal_name_hints": []},
        "pages": [{"url": "https://x/", "forms": [
            {"pii_kinds": ["email"], "consent_checkboxes": []}]}],
        "policy_documents": [],
    }


def test_ru_compliant_no_violation():
    r = la._analyze_geo(_pii_crawl(country="RU"))
    infra = r["infrastructure_and_geo"]
    assert infra["server_country"] == "RU"
    assert infra["server_country_ru"] == "Россия"
    assert infra["localization_status"] == "compliant"
    assert r["violations"] == []


def test_foreign_pii_emits_server_outside_rf():
    r = la._analyze_geo(_pii_crawl(country="US"))
    assert r["infrastructure_and_geo"]["localization_status"] == "non_compliant"
    assert [v["type"] for v in r["violations"]] == ["server_outside_rf"]


def test_cdn_edge_no_blind_fine():
    # За рубежом, но это CDN-узел → статус non_compliant, но штраф НЕ выписываем.
    r = la._analyze_geo(_pii_crawl(country="US", is_cdn=True))
    assert r["infrastructure_and_geo"]["localization_status"] == "non_compliant"
    assert r["violations"] == []


def test_no_ip_unknown():
    r = la._analyze_geo(_pii_crawl(country=None, ip=None))
    assert r["infrastructure_and_geo"]["localization_status"] == "unknown"
    assert r["violations"] == []


def test_foreign_but_no_pii_no_violation():
    crawl = _pii_crawl(country="US")
    crawl["summary"]["forms_collecting_pii"] = 0
    crawl["summary"]["forms_pii_without_consent"] = 0
    crawl["pages"] = [{"url": "https://x/", "forms": []}]
    r = la._analyze_geo(crawl)
    assert r["violations"] == []  # не оператор ПДн → нет server_outside_rf


def test_deterministic():
    crawl = _pii_crawl(country="US")
    assert la._analyze_geo(crawl) == la._analyze_geo(crawl)
