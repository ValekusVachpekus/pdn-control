"""MVP v2: cookie target_role fix, точки сбора ПДн, роль→разбивка скоринга.

Регрессионные локи под фидбэк заказчика Sprint 5:
  - cookie-нарушения адресованы МАРКЕТОЛОГУ (а не разработчику);
  - `data_collection_points` перечисляет формы со сбором ПДн для блока UI;
  - target_role управляет разбивкой score (юр. vs тех.), а cookie идёт в технический.

Чистые функции — БД/LLM/Redis не нужны.
"""
from __future__ import annotations

import os
import uuid

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://pdn:pdn@127.0.0.1:5432/pdn")
os.environ.setdefault("JWT_SECRET", "test-test-test-test-test-test-test")
os.environ.setdefault("LLM_API_KEY", "")

from app.services import violation_catalog as vc  # noqa: E402
from app.services.report_builder import (  # noqa: E402
    _data_collection_points,
    assemble,
)


def _crawl_cookie_no_reject() -> dict:
    """Cookie-баннер есть, кнопки отказа нет; PII-форм нет."""
    return {
        "meta": {"status": "ok", "pages_crawled": 1, "base_domain": "example.ru",
                 "requested_url": "example.ru", "start_url": "https://example.ru/",
                 "duration_ms": 1000, "parser_version": "test"},
        "summary": {
            "has_cookie_banner": True, "cookie_banner_has_reject": False,
            "has_privacy_policy": True, "forms_total": 0, "forms_collecting_pii": 0,
            "forms_pii_without_consent": 0, "forms_with_prechecked_consent": 0,
            "tracking_before_consent": False, "has_cross_border_transfer": False,
            "third_party_domain_count": 0, "third_party_domains": [], "trackers": [],
            "privacy_policy_urls": [],
        },
        "site_identity": {"legal_name_hints": [], "inn": [], "ogrn": [],
                          "contact_emails": [], "contact_phones": []},
        "policy_documents": [],
        "pages": [{"url": "https://example.ru/", "forms": []}],
    }


# ─── cookie target_role = marketer (фидбэк заказчика) ────────────────────────

def test_cookie_specs_target_marketer():
    # Лок каталога: cookie-нарушения адресованы маркетологу.
    for t in ("cookie_no_reject", "no_cookie_notice"):
        spec = vc.spec_for(t)
        assert spec is not None
        assert spec["target_role"] == "marketer", t


def test_cookie_no_reject_detected_and_routed_to_marketer():
    crawl = _crawl_cookie_no_reject()
    mech = vc.detect_mechanical(crawl)
    types = {v["type"] for v in mech}
    assert "cookie_no_reject" in types

    report = assemble(crawl, {"violations": mech}, report_id=uuid.uuid4())
    v = next(v for v in report["violations"] if v["type"] == "cookie_no_reject")
    assert v["target_role"] == "marketer"


# ─── data collection points (issue #102, бэкенд-строитель) ───────────────────

def test_data_collection_points_lists_pii_forms_only():
    crawl = {"pages": [
        {"url": "https://x.ru/", "forms": [
            {"action": "/lead", "pii_kinds": ["name", "phone"],
             "fields": [{"name": "name"}, {"name": "phone"}, {"name": None}]},
            {"action": "/search", "pii_kinds": [], "fields": [{"name": "q"}]},  # без ПДн → пропуск
        ]},
        {"url": "https://x.ru/contacts", "forms": [
            {"action": None, "pii_kinds": ["email"], "fields": [{"name": "email"}]},
        ]},
    ]}
    points = _data_collection_points(crawl)
    assert len(points) == 2                              # форма поиска отсеяна
    assert points[0]["url"] == "https://x.ru/"
    assert points[0]["form_name"] == "/lead"
    assert points[0]["fields"] == ["name", "phone"]      # None-поля отброшены
    assert points[1]["form_name"] is None                # нет action → None


# ─── target_role управляет разбивкой скоринга ────────────────────────────────

def test_cookie_violation_counts_as_technical_not_legal():
    crawl = _crawl_cookie_no_reject()
    mech = vc.detect_mechanical(crawl)
    report = assemble(crawl, {"violations": mech}, report_id=uuid.uuid4())
    scoring = report["scoring"]
    # cookie = маркетолог → технический балл просел, юридический остался идеальным.
    assert scoring["legal_score"] == 100
    assert scoring["technical_score"] < 100
    assert scoring["overall_score"] < 100
