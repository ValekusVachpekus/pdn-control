"""Интеграция: факты парсера → rule-engine → единый отчёт (Контракт №2).

Покрывает связку компонентов из scope #71 «parser JSON → rule-engine → unified
report JSON» БЕЗ внешних сервисов (ни БД, ни Redis, ни LLM): прогоняем crawl-факты
через детерминированный детектор нарушений (`violation_catalog.detect_mechanical`)
и сборку отчёта (`report_builder.assemble`), проверяя, что механическое нарушение
доезжает до итогового JSON с проставленными статьёй/штрафом/severity.

Чистые функции — контейнеры не нужны.
"""
from __future__ import annotations

import os
import uuid

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://pdn:pdn@127.0.0.1:5432/pdn")
os.environ.setdefault("JWT_SECRET", "test-test-test-test-test-test-test")
os.environ.setdefault("LLM_API_KEY", "")

from app.services import report_builder, violation_catalog as vc  # noqa: E402


def _crawl_with_pii_form_without_consent() -> dict:
    """Минимальный crawl: форма собирает ПДн без чекбокса согласия."""
    return {
        "meta": {
            "requested_url": "example.ru",
            "start_url": "https://example.ru/",
            "base_domain": "example.ru",
            "status": "ok",
            "pages_crawled": 1,
            "duration_ms": 1000,
            "parser_version": "test",
        },
        "summary": {
            "has_privacy_policy": False,
            "privacy_policy_urls": [],
            "has_cookie_banner": False,
            "cookie_banner_has_reject": False,
            "forms_total": 1,
            "forms_collecting_pii": 1,
            "forms_pii_without_consent": 1,
            "forms_with_prechecked_consent": 0,
            "has_cross_border_transfer": False,
            "third_party_domain_count": 0,
            "third_party_domains": [],
            "trackers": [],
        },
        "site_identity": {
            "legal_name_hints": [], "inn": [], "ogrn": [],
            "contact_emails": [], "contact_phones": [],
        },
        "policy_documents": [],
        "pages": [{
            "url": "https://example.ru/",
            "forms": [{
                "action": "/send", "method": "post", "pii_kinds": ["name", "phone"],
                "fields": [{"name": "name"}, {"name": "phone"}],
                "consent_checkboxes": [],
            }],
        }],
    }


def test_rule_engine_emits_form_without_consent():
    crawl = _crawl_with_pii_form_without_consent()
    mechanical = vc.detect_mechanical(crawl)
    types = {v["type"] for v in mechanical}
    assert "form_without_consent" in types


def test_pipeline_crawl_to_unified_report():
    crawl = _crawl_with_pii_form_without_consent()
    mechanical = vc.detect_mechanical(crawl)

    report = report_builder.assemble(
        crawl, {"violations": mechanical}, report_id=uuid.uuid4(),
    )

    # Конверт Контракта №2 на месте.
    for key in ("document_meta", "scoring", "executive_summary",
                "violations", "technical_appendix"):
        assert key in report, f"в отчёте нет {key}"

    # Механическое нарушение доехало и обогащено каталогом (статья/штраф/severity).
    v = next((v for v in report["violations"] if v["type"] == "form_without_consent"), None)
    assert v is not None, "form_without_consent не попал в итоговый отчёт"
    assert v.get("severity") in {"critical", "warning", "info"}
    assert v.get("article_152fz")
    assert int(v.get("fine_rub") or 0) >= 0

    # Точки сбора ПДн отражены в техническом приложении.
    assert isinstance(report["technical_appendix"]["data_collection_points"], list)


def test_failed_crawl_yields_empty_report_no_fabrication():
    # Парсер не зашёл на сайт → отчёт без нарушений (никакой фабрикации).
    crawl = _crawl_with_pii_form_without_consent()
    crawl["meta"]["status"] = "failed"
    crawl["meta"]["pages_crawled"] = 0
    report = report_builder.assemble(crawl, {"violations": []}, report_id=uuid.uuid4())
    assert report["violations"] == []
