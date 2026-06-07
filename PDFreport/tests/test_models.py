"""Тесты валидации входного JSON (Контракт №2)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from models import Report


def test_valid_example(example):
    report = Report.model_validate(example)
    assert report.document_meta.domain == "klinika-zdorovie.ru"
    assert len(report.violations) == 6


def test_missing_required_field(example):
    del example["scoring"]
    with pytest.raises(ValidationError):
        Report.model_validate(example)


def test_trackers_list_alias_roundtrip(example):
    """Ключ контракта `list` сохраняется при сериализации (внутри он `items`).

    Элементы списка — объекты-трекеры {name, host, origin, kind}.
    """
    report = Report.model_validate(example)
    dumped = report.model_dump(mode="json", by_alias=True)
    tracker_list = dumped["technical_appendix"]["trackers_summary"]["list"]
    assert [t["name"] for t in tracker_list] == [
        "Яндекс.Метрика",
        "Google Tag Manager",
        "JivoSite",
    ]
    assert tracker_list[0]["origin"] == "ru"
    assert tracker_list[1]["origin"] == "foreign"


def test_fine_fields(example):
    """Суммы штрафов: total_fine_rub и per-violation fine_rub читаются и опциональны."""
    report = Report.model_validate(example)
    assert report.executive_summary.total_fine_rub == 2300000
    assert report.violations[0].fine_rub == 700000
    # поля необязательны — без них валидация проходит, значения None
    del example["executive_summary"]["total_fine_rub"]
    for v in example["violations"]:
        v.pop("fine_rub", None)
    report2 = Report.model_validate(example)
    assert report2.executive_summary.total_fine_rub is None
    assert report2.violations[0].fine_rub is None


def test_extra_fields_allowed(example):
    """Бэкенд может прислать лишние поля — это не должно ломать валидацию."""
    example["document_meta"]["custom_field"] = "value"
    report = Report.model_validate(example)
    assert report.model_dump()["document_meta"]["custom_field"] == "value"
