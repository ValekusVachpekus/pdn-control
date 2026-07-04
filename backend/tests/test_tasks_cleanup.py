"""Проверка, что периодическая чистка OTP-кодов зарегистрирована и расписана.

DELETE-логику без БД не прогнать, но проверяем «проводку»: задача
auth.cleanup_email_codes зарегистрирована в Celery и стоит в beat-расписании —
иначе чистка просто не запустится.
"""
from __future__ import annotations

import os

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://pdn:pdn@127.0.0.1:5432/pdn")
os.environ.setdefault("JWT_SECRET", "test-test-test-test-test-test-test")
os.environ.setdefault("LLM_API_KEY", "")

from app.workers import tasks  # noqa: E402,F401 — импорт регистрирует задачи
from app.workers.celery_app import celery_app  # noqa: E402


def test_cleanup_task_registered():
    assert "auth.cleanup_email_codes" in celery_app.tasks


def test_cleanup_in_beat_schedule():
    entry = celery_app.conf.beat_schedule.get("cleanup-email-codes")
    assert entry is not None
    assert entry["task"] == "auth.cleanup_email_codes"
