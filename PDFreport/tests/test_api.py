"""Тесты HTTP-эндпоинтов сервиса."""

from __future__ import annotations

import shutil

import pytest
from fastapi.testclient import TestClient

from service import app

client = TestClient(app)

needs_typst = pytest.mark.skipif(
    shutil.which("typst") is None, reason="typst не установлен"
)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_render_invalid_returns_422():
    resp = client.post("/render", json={"document_meta": {}})
    assert resp.status_code == 422


@needs_typst
def test_render_example_returns_pdf(example):
    resp = client.post("/render", json=example)
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert resp.content[:5] == b"%PDF-"
