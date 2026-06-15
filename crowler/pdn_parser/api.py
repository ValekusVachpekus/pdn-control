"""HTTP-микросервис парсера ПДн Контроль.

Бэкенд шлёт POST /scan с URL сайта и получает в ответ JSON-конверт (schema 1.2),
тот же, что отдаёт CLI. Парсер фактов — без юридических выводов.

Запуск:
    uvicorn pdn_parser.api:app --host 0.0.0.0 --port 8010

Переменные окружения:
    MAX_CONCURRENT_SCANS  — сколько проверок выполнять одновременно (по умолчанию 2)
    SCAN_TIMEOUT_SEC      — жёсткий лимит на одну проверку, сек (по умолчанию 300)
"""

from __future__ import annotations

import asyncio
import json
import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from . import schema_path
from .crawler import PARSER_VERSION, crawl_site
from .models import SCHEMA_VERSION

MAX_CONCURRENT_SCANS = int(os.getenv("MAX_CONCURRENT_SCANS", "2"))
SCAN_TIMEOUT_SEC = int(os.getenv("SCAN_TIMEOUT_SEC", "300"))
# Запас между мягким бюджетом обхода и жёстким таймаутом: цикл должен сам
# остановиться и финализировать партиал ДО того, как asyncio.wait_for убьёт скан.
_TIMEOUT_SAFETY_MARGIN_SEC = 30

app = FastAPI(
    title="ПДн Контроль — парсер",
    version=PARSER_VERSION,
    description="Микросервис: принимает URL сайта, возвращает факты для аудита 152-ФЗ.",
)

# Ограничиваем число одновременных проверок — каждая поднимает свой браузер.
_scan_semaphore = asyncio.Semaphore(MAX_CONCURRENT_SCANS)

# JSON Schema читаем один раз при старте.
with open(schema_path(), encoding="utf-8") as _fh:
    _SCHEMA = json.load(_fh)


class ScanRequest(BaseModel):
    url: str = Field(..., description="URL сайта (схема не обязательна)", examples=["example.ru"])
    max_pages: int = Field(20, ge=1, le=200)
    max_depth: int = Field(2, ge=0, le=5)
    respect_robots: bool = True
    page_timeout_ms: int = Field(20_000, ge=1_000, le=120_000)
    scan_id: str | None = None


@app.get("/health")
async def health() -> dict:
    return {
        "status": "ok",
        "parser_version": PARSER_VERSION,
        "schema_version": SCHEMA_VERSION,
        "max_concurrent_scans": MAX_CONCURRENT_SCANS,
    }


@app.get("/schema")
async def schema() -> dict:
    """JSON Schema ответа /scan (для валидации и генерации типов на бэке)."""
    return _SCHEMA


@app.post("/scan")
async def scan(req: ScanRequest) -> dict:
    """Обойти сайт и вернуть JSON-конверт с фактами (schema 1.2)."""
    async with _scan_semaphore:
        try:
            result = await asyncio.wait_for(
                crawl_site(
                    req.url,
                    requested_url=req.url,
                    scan_id=req.scan_id,
                    max_pages=req.max_pages,
                    max_depth=req.max_depth,
                    respect_robots=req.respect_robots,
                    headless=True,
                    page_timeout_ms=req.page_timeout_ms,
                    time_budget_sec=SCAN_TIMEOUT_SEC - _TIMEOUT_SAFETY_MARGIN_SEC,
                ),
                timeout=SCAN_TIMEOUT_SEC,
            )
        except asyncio.TimeoutError:
            raise HTTPException(
                status_code=504,
                detail=f"Проверка превысила лимит {SCAN_TIMEOUT_SEC} c. "
                       f"Уменьшите max_pages или увеличьте SCAN_TIMEOUT_SEC.",
            )
        except Exception as exc:  # noqa: BLE001 — наружу отдаём безопасный текст
            raise HTTPException(status_code=500, detail=f"Ошибка парсера: {exc}")

    return result.to_dict()
