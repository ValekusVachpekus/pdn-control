"""Тест компиляции PDF через Typst."""

from __future__ import annotations

import shutil

import pytest

from renderer import render_pdf

needs_typst = pytest.mark.skipif(
    shutil.which("typst") is None, reason="typst не установлен"
)


@needs_typst
def test_render_pdf_returns_pdf_bytes(example):
    pdf = render_pdf(example)
    assert pdf[:5] == b"%PDF-"
    assert len(pdf) > 1000
