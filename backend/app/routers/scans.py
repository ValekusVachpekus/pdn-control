"""POST /api/scans — поставить сайт в очередь проверки.

Сохраняем запись в БД со статусом pending, ставим Celery-таск, возвращаем report_id.
Лимиты страниц зависят от тарифа (free vs paid).
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import get_settings
from ..db import get_session
from ..deps import get_current_user
from ..models.scan import Scan, ScanStatus
from ..models.user import User
from ..plans import is_paid
from ..schemas.scan import ScanCreateIn, ScanCreateOut, ScanStatusOut, normalize_domain
from ..workers.tasks import run_scan

router = APIRouter(prefix="/api/scans", tags=["scans"])


@router.post("", response_model=ScanCreateOut, status_code=status.HTTP_201_CREATED)
async def create_scan(
    body: ScanCreateIn,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ScanCreateOut:
    s = get_settings()
    max_pages = s.paid_max_pages if is_paid(user.plan) else s.free_max_pages

    domain = normalize_domain(body.url)
    scan = Scan(user_id=user.id, url=body.url, domain=domain, status=ScanStatus.pending)
    session.add(scan)
    await session.flush()

    # Ставим в очередь. Коммит произойдёт через зависимость get_session.
    # Если воркер успеет схватить таск раньше коммита — он ничего не найдёт; коммитим заранее.
    await session.commit()

    run_scan.delay(str(scan.id), body.url, max_pages=max_pages, llm_enabled=is_paid(user.plan))

    return ScanCreateOut(report_id=scan.id)


@router.get("/{scan_id}/status", response_model=ScanStatusOut)
async def scan_status(
    scan_id: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ScanStatusOut:
    import uuid

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
