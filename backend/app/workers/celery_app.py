"""Celery-приложение. Запуск воркера:

    celery -A app.workers.celery_app worker --loglevel=info --concurrency=2
"""
from __future__ import annotations

from celery import Celery
from celery.schedules import crontab

from ..config import get_settings

_settings = get_settings()

celery_app = Celery(
    "pdn_backend",
    broker=_settings.celery_broker_url,
    backend=_settings.celery_result_backend,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,  # парсер тяжёлый — берём задачи по одной
    task_default_queue="scans",
    timezone="UTC",
)

# Периодические задачи (celery beat). Воркер запускается с флагом -B
# (embedded beat) — отдельный контейнер не нужен, воркер один.
celery_app.conf.beat_schedule = {
    # Чистим отработавшие OTP-коды (использованные/протухшие) раз в 6 часов,
    # чтобы таблица email_codes не копила мёртвые строки.
    "cleanup-email-codes": {
        "task": "auth.cleanup_email_codes",
        "schedule": crontab(minute=0, hour="*/6"),
    },
}
