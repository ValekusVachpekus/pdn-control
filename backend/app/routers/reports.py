"""GET /api/reports/:id      — JSON Контракта №2 (на free-тарифе обрезанный).
GET /api/reports/:id/pdf  — PDF, доступно только при scan.paid=True.

Free-режим возвращает усечённый отчёт: оставляем только то, что фронт показывает
на тизере (score, verdict, stats, total fine). Детали нарушений, infrastructure_and_geo
и technical_appendix скрыты до оплаты — это серверный gate, а не клиентский blur.
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


def _free_view(report: dict) -> dict:
    """Усечённый JSON для бесплатного режима — только то, что фронт показывает
    выше fold'а (заголовок, рисковая шкала, executive summary, сводные счётчики)."""
    es = report.get("executive_summary", {}) or {}
    violations = report.get("violations", []) or []
    # Из деталей оставляем только id/severity/article/title — без description,
    # evidence, recommendation и fine_rub. Этого достаточно, чтобы фронт показал
    # список заблюренных карточек с шапками, но не раскрыл, что именно нашли.
    minimal_violations = [
        {
            "id": v.get("id"),
            "severity": v.get("severity"),
            "article_152fz": v.get("article_152fz"),
            "title": v.get("title"),
            "target_role": v.get("target_role"),
        }
        for v in violations
    ]
    return {
        "document_meta": report.get("document_meta", {}),
        "scoring": report.get("scoring", {}),
        "executive_summary": {
            "verdict": es.get("verdict"),
            "verdict_plain": es.get("verdict_plain"),
            "stats": es.get("stats", {}),
            "total_fine_rub": es.get("total_fine_rub"),
            "passed_checks": es.get("passed_checks", []),
        },
        # Детали — заглушки, чтобы фронту было что отрисовать в "запертом" виде.
        "infrastructure_and_geo": {
            "server_ip": None, "server_country": None, "server_country_ru": None,
            "hosting_provider": None, "localization_compliant": False, "localization_note": None,
        },
        "violations": minimal_violations,
        "technical_appendix": {
            "documents_found": [], "trackers_summary": {"total": 0, "russian": 0, "foreign": 0, "list": []},
            "data_collection_points": [], "ai_analysis": [],
        },
        # Спец-маркер для фронта: «это тизер, нужна оплата».
        "_paid": False,
    }


def _scan_failed_synthetic(scan: Scan) -> dict:
    """Synthetic-отчёт для скана со status=failed (worker крашнулся, парсер
    таймаутнул, orphan-cleanup). Без этого фронт получает 409 и крутит спиннер
    до 3 минут polling'а."""
    return {
        "_scan_failed": True,
        "_paid": False,
        "_ai_powered": False,
        "document_meta": {
            "report_id": str(scan.id),
            "generated_at": (scan.finished_at or scan.created_at).isoformat(),
            "target_url": scan.url,
            "domain": scan.domain,
            "organization_name": None,
            "scan_duration_sec": None,
            "pages_scanned": 0,
            "scanner_version": None,
        },
        "scoring": {
            "overall_score": None, "risk_level": "UNKNOWN",
            "risk_label_ru": "Не выполнен",
            "legal_score": None, "technical_score": None,
        },
        "executive_summary": {
            "verdict": f"Проверка не выполнена. {scan.error or 'Внутренняя ошибка.'}",
            "verdict_plain": "Не удалось выполнить проверку сайта. Попробуйте запустить её ещё раз.",
            "stats": {"critical_count": 0, "warning_count": 0, "info_count": 0, "passed_count": 0},
            "total_fine_rub": 0,
            "passed_checks": [],
        },
        "infrastructure_and_geo": {
            "server_ip": None, "server_country": None, "server_country_ru": None,
            "hosting_provider": None, "localization_compliant": False,
            "localization_status": "unknown", "localization_note": None,
        },
        "violations": [],
        "technical_appendix": {
            "documents_found": [],
            "trackers_summary": {"total": 0, "russian": 0, "foreign": 0, "list": []},
            "data_collection_points": [], "ai_analysis": [],
        },
    }


@router.get("/{scan_id}")
async def get_report(
    scan_id: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    scan = await _load_scan(scan_id, user, session)

    # Скан в очереди / выполняется — 409, фронт polls.
    if scan.status in (ScanStatus.pending, ScanStatus.running):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"report not ready (status={scan.status.value})",
        )

    # Скан упал — отдаём синтетический «не выполнен» отчёт, фронт покажет банер.
    if scan.status == ScanStatus.failed or not scan.report_json:
        return _scan_failed_synthetic(scan)

    if scan.paid:
        return {**scan.report_json, "_paid": True}
    # Failed-отчёт от rule-engine (парсер зашёл, но 0 страниц) сохранён в JSON
    # с _scan_failed=true — пропускаем без обрезаний, чтобы фронт показал банер.
    if scan.report_json.get("_scan_failed"):
        return {**scan.report_json, "_paid": False}
    return _free_view(scan.report_json)


@router.get("/{scan_id}/pdf")
async def get_report_pdf(
    scan_id: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Response:
    scan = await _load_scan(scan_id, user, session)
    if not scan.paid:
        # 402 — фронт показывает кнопку «Разблокировать отчёт».
        raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail="payment required")
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
