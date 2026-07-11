"""FastAPI-приложение ПДн Контроль (backend API)."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import update

from . import __version__
from .config import get_settings
from .db import SessionLocal
from .models.scan import Scan, ScanStatus
from .routers import auth, billing, health, reports, scans

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger(__name__)

settings = get_settings()

# После любого рестарта (или падения воркера) сканы со статусом running, чья
# Celery-задача больше не выполняется, остаются «зомби» — фронт виснет на них
# навсегда. Чистим их при старте API: всё что в running > этого порога — failed.
ORPHAN_RUNNING_THRESHOLD_MIN = 15


# Swagger/OpenAPI открываем только в dev — в проде это лишнее раскрытие всех эндпоинтов.
_docs_enabled = settings.app_env == "dev"
app = FastAPI(
    title="ПДн Контроль — API",
    version=__version__,
    description="Backend API: регистрация/логин, проверки сайтов, отчёты (Контракт №2), биллинг.",
    docs_url="/docs" if _docs_enabled else None,
    redoc_url="/redoc" if _docs_enabled else None,
    openapi_url="/openapi.json" if _docs_enabled else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(scans.router)
app.include_router(reports.router)
app.include_router(billing.router)


@app.on_event("startup")
async def _mark_orphan_scans_failed() -> None:
    """Помечаем зависшие running-сканы как failed после рестарта."""
    threshold = datetime.now(timezone.utc) - timedelta(minutes=ORPHAN_RUNNING_THRESHOLD_MIN)
    async with SessionLocal() as session:
        result = await session.execute(
            update(Scan)
            .where(Scan.status == ScanStatus.running, Scan.created_at < threshold)
            .values(
                status=ScanStatus.failed,
                error=f"orphan: timed out after {ORPHAN_RUNNING_THRESHOLD_MIN} min in running",
                finished_at=datetime.now(timezone.utc),
            )
        )
        await session.commit()
        if result.rowcount:
            log.warning("marked %d orphan running scans as failed", result.rowcount)
