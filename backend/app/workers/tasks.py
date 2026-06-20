"""Фоновая задача проверки сайта.

Новый пайплайн (без rule-engine):
    1. crawler → CrawlJSON (Контракт №1)
    2. lookup в Redis: вернёт ли там готовый LLM-output для этого crawl
    3. cache miss → llm_analyzer.call_llm(crawl) → JSON со всеми юр-вердиктами,
       сохраняем в кеш (TTL 7 дней)
    4. report_builder.assemble(crawl, llm_output) → готовый Контракт №2
    5. сохраняем в Scan.report_json

Если на любом из шагов 1-4 происходит фатальная ошибка — скан помечается
failed. Никаких fallback'ов на детерминированные правила нет (по требованию
заказчика: все вердикты должна выносить LLM).
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
from ..services import llm_cache, scan_progress
from ..services.crawler_client import CrawlerError, scan_site_sync
from ..services.llm_analyzer import LLMError, call_llm
from ..services.report_builder import assemble
from .celery_app import celery_app

log = logging.getLogger(__name__)


def _sync_db_url(url: str) -> str:
    """asyncpg-URL → psycopg2-URL для синхронного драйвера в воркере."""
    return url.replace("+asyncpg", "+psycopg2")


def _make_session() -> Session:
    s = get_settings()
    engine = create_engine(_sync_db_url(s.database_url), pool_pre_ping=True, future=True)
    return sessionmaker(engine, expire_on_commit=False, future=True)()


def _mark_failed(session: Session, sid: uuid.UUID, error: str) -> dict:
    session.execute(
        update(Scan).where(Scan.id == sid).values(
            status=ScanStatus.failed,
            error=error[:2000],
            finished_at=datetime.now(timezone.utc),
        )
    )
    session.commit()
    scan_progress.set_phase(str(sid), "failed", error=error[:300])
    return {"status": "failed", "error": error}


@celery_app.task(bind=True, name="scans.run", max_retries=0)
def run_scan(self: Task, scan_id: str, url: str, *, max_pages: int, llm_enabled: bool = True) -> dict:
    """Полный цикл проверки одного сайта.

    llm_enabled оставлено в сигнатуре для обратной совместимости со старым
    кодом, который мог его передавать. В новом пайплайне LLM используется
    всегда (на нём держится весь юр-анализ); если ключ не сконфигурирован,
    скан помечается failed.
    """
    del llm_enabled  # больше не управляется на уровне таска
    sid = uuid.UUID(scan_id)
    session = _make_session()
    try:
        # 1) Помечаем running + фаза «обход страниц»
        session.execute(
            update(Scan).where(Scan.id == sid).values(status=ScanStatus.running)
        )
        session.commit()
        scan_progress.set_phase(scan_id, "crawling", url=url)

        # 2) Парсер
        try:
            crawl = scan_site_sync(url, max_pages=max_pages)
        except CrawlerError as exc:
            log.exception("crawler failed for scan %s", sid)
            return _mark_failed(session, sid, str(exc))

        meta = crawl.get("meta", {}) or {}
        summary = crawl.get("summary", {}) or {}
        pages_crawled = meta.get("pages_crawled") or 0

        # Реальные счётчики от парсера — показываем их во время LLM-анализа.
        facts = {
            "pages": pages_crawled,
            "forms": summary.get("forms_total") or 0,
            "forms_pii": summary.get("forms_collecting_pii") or 0,
            "trackers": len(summary.get("trackers") or []),
            "third_party_domains": summary.get("third_party_domain_count") or 0,
            "has_policy": bool(summary.get("has_privacy_policy")),
            "server_ip": meta.get("server_ip"),
        }

        # 3) LLM — пропускаем если парсер ничего не получил (assemble тогда
        # сам отдаст «не проверено», вызывать LLM на пустом crawl бессмысленно).
        llm_output: dict | None = None
        if pages_crawled > 0:
            scan_progress.set_phase(scan_id, "analyzing", **facts)
            llm_output = llm_cache.get(crawl)
            if llm_output is not None:
                log.info("LLM cache hit for scan %s", sid)
            else:
                log.info("LLM cache miss for scan %s — calling LLM", sid)
                try:
                    llm_output = call_llm(crawl)
                except LLMError as exc:
                    log.exception("LLM failed for scan %s", sid)
                    return _mark_failed(session, sid, f"LLM error: {exc}")
                llm_cache.set_(crawl, llm_output)

        # 4) Сборка Контракта №2
        scan_progress.set_phase(scan_id, "building", **facts)
        report = assemble(crawl, llm_output, report_id=sid)

        # 5) Сохраняем готовый отчёт
        session.execute(
            update(Scan).where(Scan.id == sid).values(
                status=ScanStatus.done,
                report_json=report,
                finished_at=datetime.now(timezone.utc),
            )
        )
        session.commit()
        scan_progress.set_phase(scan_id, "done", **facts)
        return {"status": "done", "scan_id": str(sid)}

    except Exception as exc:  # noqa: BLE001 — самый внешний catch для надёжности
        log.exception("scan %s crashed", sid)
        return _mark_failed(session, sid, f"internal: {exc}")
    finally:
        session.close()
