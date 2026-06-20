"""Общие фикстуры для тестов."""

from __future__ import annotations

import json
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent


@pytest.fixture
def example() -> dict:
    """Пример входного JSON по Контракту №2 (PDFreport/example.json)."""
    return json.loads((ROOT / "example.json").read_text(encoding="utf-8"))
