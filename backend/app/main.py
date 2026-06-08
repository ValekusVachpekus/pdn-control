"""FastAPI-приложение ПДн Контроль (backend API)."""
from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import __version__
from .config import get_settings
from .routers import auth, billing, health, reports, scans

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

settings = get_settings()

app = FastAPI(
    title="ПДн Контроль — API",
    version=__version__,
    description="Backend API: регистрация/логин, проверки сайтов, отчёты (Контракт №2), биллинг.",
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
