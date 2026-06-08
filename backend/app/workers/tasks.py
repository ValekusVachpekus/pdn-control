"""Фоновая задача проверки сайта.

Один таск = одна проверка. Сначала бьёмся в crawler (8010), получаем факты по
Контракту №1, прогоняем rule-engine и сохраняем итог (Контракт №2) в БД.
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from celery import Task
from sqlalchemy import create_engine, update
from sqlalchemy.orm import Session, sessionmaker

from ..config import get_settings
from ..models.scan import Scan, ScanStatus
from ..services.crawler_client import CrawlerError, scan_site_sync
from ..services.llm import analyze as llm_analyze
from ..services.rule_engine import build_report
from .celery_app import celery_app

log = logging.getLogger(__name__)


def _sync_db_url(url: str) -> str:
    """asyncpg-URL → psycopg2-URL для синхронного драйвера в воркере."""
    return url.replace("+asyncpg", "+psycopg2")


def _make_session() -> Session:
    s = get_settings()
    engine = create_engine(_sync_db_url(s.database_url), pool_pre_ping=True, future=True)
    return sessionmaker(engine, expire_on_commit=False, future=True)()


@celery_app.task(bind=True, name="scans.run", max_retries=0)
def run_scan(self: Task, scan_id: str, url: str, *, max_pages: int, llm_enabled: bool = False) -> dict:
    """Полный цикл проверки одного сайта."""
    sid = uuid.UUID(scan_id)
    session = _make_session()
    try:
        # 1) Помечаем как running
        session.execute(
            update(Scan).where(Scan.id == sid).values(status=ScanStatus.running)
        )
        session.commit()

        # 2) Парсер
        try:
            crawl = scan_site_sync(url, max_pages=max_pages)
        except CrawlerError as exc:
            log.exception("crawler failed for scan %s", sid)
            session.execute(
                update(Scan)
                .where(Scan.id == sid)
                .values(
                    status=ScanStatus.failed,
                    error=str(exc),
                    finished_at=datetime.now(timezone.utc),
                )
            )
            session.commit()
            return {"status": "failed", "error": str(exc)}

        # 3) Rule-engine: факты → Контракт №2
        report = build_report(crawl, report_id=sid)

        # 3.5) LLM-анализ текстов политик (только для paid). Не падаем при ошибке.
        if llm_enabled:
            try:
                notes = llm_analyze(crawl)
                if notes:
                    report["technical_appendix"]["ai_analysis"] = notes
            except Exception:  # noqa: BLE001
                log.exception("LLM analyze failed for scan %s", sid)

        # 4) Сохраняем готовый отчёт
        session.execute(
            update(Scan)
            .where(Scan.id == sid)
            .values(
                status=ScanStatus.done,
                report_json=report,
                finished_at=datetime.now(timezone.utc),
            )
        )
        session.commit()
        return {"status": "done", "scan_id": str(sid)}
    except Exception as exc:  # noqa: BLE001
        log.exception("scan %s crashed", sid)
        session.execute(
            update(Scan)
            .where(Scan.id == sid)
            .values(
                status=ScanStatus.failed,
                error=f"internal: {exc}",
                finished_at=datetime.now(timezone.utc),
            )
        )
        session.commit()
        return {"status": "failed", "error": str(exc)}
    finally:
        session.close()
