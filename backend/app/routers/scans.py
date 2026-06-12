"""POST /api/scans — поставить сайт в очередь проверки.

Тарифов нет: все пользователи получают полный обход (paid_max_pages) и LLM-анализ
текстов политик. Видимость деталей в отчёте — отдельно, через scan.paid (см.
маршрут /api/reports/{id}).
"""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import get_settings
from ..db import get_session
from ..deps import get_current_user
from ..models.scan import Scan, ScanStatus
from ..models.user import User
from ..schemas.scan import ScanCreateIn, ScanCreateOut, ScanStatusOut, normalize_domain
from ..services import scan_progress
from ..workers.tasks import run_scan

router = APIRouter(prefix="/api/scans", tags=["scans"])


@router.post("", response_model=ScanCreateOut, status_code=status.HTTP_201_CREATED)
async def create_scan(
    body: ScanCreateIn,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ScanCreateOut:
    s = get_settings()
    domain = normalize_domain(body.url)
    scan = Scan(user_id=user.id, url=body.url, domain=domain, status=ScanStatus.pending)
    session.add(scan)
    await session.flush()
    # Коммитим до постановки таска, иначе воркер не увидит запись.
    await session.commit()

    # Начальная фаза «в очереди» — фронт сразу видит реальный статус,
    # не дожидаясь, пока воркер возьмёт задачу.
    scan_progress.set_phase(str(scan.id), "queued")
    run_scan.delay(str(scan.id), body.url, max_pages=s.paid_max_pages, llm_enabled=True)

    return ScanCreateOut(report_id=scan.id)


@router.get("", response_model=list[dict])
async def list_scans(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> list[dict]:
    """История сканов пользователя (последние первыми).

    Для каждого скана возвращаем то, что нужно фронту для списка истории:
    мета (домен, дата, статус, paid-флаг) + краткая оценка из report_json
    (score, risk_level, счётчики), если отчёт уже готов.
    """
    rows = await session.scalars(
        select(Scan)
        .where(Scan.user_id == user.id)
        .order_by(desc(Scan.created_at))
        .limit(limit).offset(offset)
    )
    out: list[dict] = []
    for s in rows:
        rj = s.report_json or {}
        scoring = rj.get("scoring") or {}
        es = rj.get("executive_summary") or {}
        stats = es.get("stats") or {}
        out.append({
            "id": str(s.id),
            "url": s.url,
            "domain": s.domain,
            "status": s.status.value,
            "paid": bool(s.paid),
            "created_at": s.created_at.isoformat(),
            "finished_at": s.finished_at.isoformat() if s.finished_at else None,
            "score": scoring.get("overall_score"),
            "risk_level": scoring.get("risk_level"),
            "risk_label_ru": scoring.get("risk_label_ru"),
            "organization": (rj.get("document_meta") or {}).get("organization_name"),
            "critical_count": stats.get("critical_count") or 0,
            "warning_count": stats.get("warning_count") or 0,
            "info_count": stats.get("info_count") or 0,
            "total_fine_rub": es.get("total_fine_rub") or 0,
            "scan_failed": bool(rj.get("_scan_failed")),
        })
    return out


@router.get("/{scan_id}/status", response_model=ScanStatusOut)
async def scan_status(
    scan_id: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ScanStatusOut:
    try:
        sid = uuid.UUID(scan_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="not found")

    scan = await session.get(Scan, sid)
    if scan is None or scan.user_id != user.id:
        raise HTTPException(status_code=404, detail="not found")

    return ScanStatusOut(
        report_id=scan.id,
        status=scan.status,
        error=scan.error,
        created_at=scan.created_at,
        finished_at=scan.finished_at,
    )


@router.get("/{scan_id}/progress")
async def scan_progress_endpoint(
    scan_id: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Реальный прогресс сканирования для экрана ожидания.

    Возвращает текущую фазу конвейера (queued → crawling → analyzing →
    building → done/failed) и реальные счётчики от парсера (страниц обойдено,
    форм, трекеров), как только они становятся известны. Данные берём из Redis;
    если их там нет (TTL истёк), отдаём фазу по статусу из БД.
    """
    try:
        sid = uuid.UUID(scan_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="not found")

    scan = await session.get(Scan, sid)
    if scan is None or scan.user_id != user.id:
        raise HTTPException(status_code=404, detail="not found")

    prog = scan_progress.get(scan_id)
    if prog is None:
        # Redis ничего не знает (TTL истёк/перезапуск) — выводим фазу из статуса БД.
        fallback = {
            ScanStatus.pending: "queued",
            ScanStatus.running: "crawling",
            ScanStatus.done: "done",
            ScanStatus.failed: "failed",
        }.get(scan.status, "queued")
        prog = {"phase": fallback}

    # status из БД — источник истины о завершённости (Redis мог отстать)
    prog["status"] = scan.status.value
    prog["phases"] = list(scan_progress.PHASES)
    return prog
