"""QRT-02 — детерминизм механического слоя нарушений (quality requirement QR-02).

Reliability / Maturity: один и тот же crawl-вход обязан давать байт-в-байт
одинаковый набор механических нарушений на повторных прогонах. Детерминизм
ограничен rule-based слоем (LLM из QR-02 исключён по построению).

Чистые функции — Redis/БД/LLM не нужны.
"""
from __future__ import annotations

import json
import os

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://pdn:pdn@127.0.0.1:5432/pdn")
os.environ.setdefault("JWT_SECRET", "test-test-test-test-test-test-test")
os.environ.setdefault("LLM_API_KEY", "")

from app.services import violation_catalog as vc  # noqa: E402

# QR-02 measure: N = 5 повторных прогонов → 0 расхождений.
N_RUNS = 5


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


def _canonical(violations) -> str:
    """Стабильная сериализация набора нарушений для побайтового сравнения."""
    return json.dumps(
        sorted(violations, key=lambda v: v.get("type", "")),
        sort_keys=True,
        ensure_ascii=False,
    )


def test_detect_mechanical_byte_identical_over_n_runs():
    """Один и тот же объект crawl, прогнанный N раз → идентичный результат."""
    crawl = _pii_crawl()
    outputs = [_canonical(vc.detect_mechanical(crawl)) for _ in range(N_RUNS)]
    assert len(set(outputs)) == 1, "механические нарушения расходятся между прогонами"
    assert json.loads(outputs[0]), "на PII-сайте ожидается непустой набор нарушений"


def test_detect_mechanical_identical_for_equal_inputs():
    """Свежий эквивалентный crawl на каждом прогоне → тот же результат
    (нет скрытого глобального состояния)."""
    outputs = [_canonical(vc.detect_mechanical(_pii_crawl())) for _ in range(N_RUNS)]
    assert len(set(outputs)) == 1, "результат зависит от идентичности объекта входа"


def test_detect_mechanical_does_not_mutate_input():
    """detect_mechanical не должен мутировать вход — иначе повторный прогон
    того же объекта дал бы другой результат."""
    crawl = _pii_crawl()
    before = json.dumps(crawl, sort_keys=True, ensure_ascii=False)
    vc.detect_mechanical(crawl)
    after = json.dumps(crawl, sort_keys=True, ensure_ascii=False)
    assert before == after, "detect_mechanical мутировал входной crawl"
