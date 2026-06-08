"""GET /api/reports/:id — JSON Контракта №2;
GET /api/reports/:id/pdf — проксирует JSON в PDF-микросервис и отдаёт PDF.
"""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_session
from ..deps import get_current_user
from ..models.scan import Scan, ScanStatus
from ..models.user import User
from ..plans import is_paid
from ..services.pdf_client import PdfError, render_pdf

router = APIRouter(prefix="/api/reports", tags=["reports"])


async def _load_scan(scan_id: str, user: User, session: AsyncSession) -> Scan:
    try:
        sid = uuid.UUID(scan_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="not found")

    scan = await session.get(Scan, sid)
    if scan is None or scan.user_id != user.id:
        raise HTTPException(status_code=404, detail="not found")
    return scan


@router.get("/{scan_id}")
async def get_report(
    scan_id: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    scan = await _load_scan(scan_id, user, session)
    if scan.status != ScanStatus.done or not scan.report_json:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"report not ready (status={scan.status.value})",
        )
    return scan.report_json


@router.get("/{scan_id}/pdf")
async def get_report_pdf(
    scan_id: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Response:
    if not is_paid(user.plan):
        raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail="upgrade required")

    scan = await _load_scan(scan_id, user, session)
    if scan.status != ScanStatus.done or not scan.report_json:
        raise HTTPException(status_code=409, detail=f"report not ready (status={scan.status.value})")

    try:
        pdf = await render_pdf(scan.report_json)
    except PdfError as exc:
        raise HTTPException(status_code=502, detail=f"pdf service error: {exc}") from exc

    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="report_{scan_id}.pdf"'},
    )
