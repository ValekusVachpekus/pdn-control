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
    """Ключ контракта `list` сохраняется при сериализации (внутри он `names`)."""
    report = Report.model_validate(example)
    dumped = report.model_dump(mode="json", by_alias=True)
    assert dumped["technical_appendix"]["trackers_summary"]["list"] == [
        "Яндекс.Метрика",
        "Google Tag Manager",
        "JivoSite",
    ]


def test_extra_fields_allowed(example):
    """Бэкенд может прислать лишние поля — это не должно ломать валидацию."""
    example["document_meta"]["custom_field"] = "value"
    report = Report.model_validate(example)
    assert report.model_dump()["document_meta"]["custom_field"] == "value"
