"""Юнит-тесты код-генерации механических нарушений (детерминизм).

Чистые функции — Redis/БД/LLM не нужны. Покрываем:
  - идемпотентность detect_mechanical (один и тот же crawl → один и тот же набор);
  - сайт без ПДн → ноль нарушений;
  - битый crawl → ноль нарушений (precondition_confirmed fail-CLOSED, без фабрикации);
  - no_rkn_notification НЕ выписывается кодом (непроверяемый факт, ложный штраф);
  - strict (генератор) vs soft (валидатор) семантика предусловий.
"""
from __future__ import annotations

import os

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://pdn:pdn@127.0.0.1:5432/pdn")
os.environ.setdefault("JWT_SECRET", "test-test-test-test-test-test-test")
os.environ.setdefault("LLM_API_KEY", "")

from app.services import violation_catalog as vc  # noqa: E402


def _pii_crawl() -> dict:
    """Сайт с формой ПДн без согласия + Яндекс.Метрика, без политики."""
    return {
        "meta": {"server_ip": "1.2.3.4"},
        "summary": {
            "has_privacy_policy": False, "forms_total": 1, "forms_collecting_pii": 1,
            "forms_pii_without_consent": 1, "pii_kinds_collected": ["email", "name", "phone"],
            "has_cookie_banner": False, "third_party_domain_count": 1,
            "trackers": [{"name": "Яндекс.Метрика", "category": "analytics", "cross_border": False}],
        },
        "site_identity": {"inn": [], "ogrn": [], "legal_name_hints": []},
        "pages": [{"url": "https://x/", "forms": [
            {"pii_kinds": ["email", "name", "phone"], "consent_checkboxes": []}]}],
        "policy_documents": [],
    }


def _clean_crawl() -> dict:
    """Статичный сайт без форм/трекеров/политики — не оператор ПДн."""
    return {
        "meta": {"server_ip": "1.2.3.4"},
        "summary": {"has_privacy_policy": False, "forms_total": 0, "forms_collecting_pii": 0,
                    "has_cookie_banner": False, "third_party_domain_count": 0, "trackers": []},
        "site_identity": {"inn": [], "ogrn": [], "legal_name_hints": []},
        "pages": [{"url": "https://x/", "forms": []}],
        "policy_documents": [],
    }


def test_detect_mechanical_idempotent():
    crawl = _pii_crawl()
    a = sorted(v["type"] for v in vc.detect_mechanical(crawl))
    b = sorted(v["type"] for v in vc.detect_mechanical(crawl))
    assert a == b
    assert a  # на PII-сайте что-то выписано


def test_no_pii_site_zero_violations():
    crawl = _clean_crawl()
    assert vc.processes_pii(crawl) is False
    assert vc.detect_mechanical(crawl) == []


def test_rkn_not_emitted_by_code():
    """no_rkn_notification непроверяем краулером → код его не выписывает."""
    types = {v["type"] for v in vc.detect_mechanical(_pii_crawl())}
    assert "no_rkn_notification" not in types
    assert "no_rkn_notification" not in vc.MECHANICAL


def test_broken_crawl_no_fabrication():
    """Битый crawl (лямбды предусловий бросают) → ноль нарушений, не фантомы."""
    broken = {"summary": "НЕ_СЛОВАРЬ", "site_identity": None, "pages": None}
    assert vc.detect_mechanical(broken) == []


def test_strict_vs_soft_precondition():
    broken = {"summary": "НЕ_СЛОВАРЬ", "site_identity": None, "pages": None}
    # генератор (strict) на ошибке → False (не выписываем)
    assert vc.precondition_confirmed("no_privacy_policy", broken) is False
    # валидатор (soft) на ошибке → True (не выбрасываем присланное LLM)
    assert vc.precondition_holds("no_privacy_policy", broken) is True
    # неизвестный тип → оба False
    assert vc.precondition_confirmed("nonexistent", _pii_crawl()) is False
    assert vc.precondition_holds("nonexistent", _pii_crawl()) is False


def test_mechanical_have_specs_and_text():
    """Каждый механический тип есть в каталоге и имеет шаблон текста."""
    for t in vc.MECHANICAL:
        assert vc.spec_for(t) is not None
        desc, rec = vc._MECH_TEXT.get(t, ("", ""))
        assert desc and rec
