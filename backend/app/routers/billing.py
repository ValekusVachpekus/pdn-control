"""Биллинг: каталог продуктов и checkout под разовую оплату конкретного отчёта.

Реальная интеграция с CloudPayments — отдельная задача:
1) бэк создаёт checkout-сессию (виджет/страницу) и возвращает её URL;
2) после успешной оплаты CloudPayments дёргает наш webhook;
3) webhook ставит scan.paid = True.

Сейчас (MVP, dev-режим) шаг 2-3 эмулируется здесь же: при вызове /checkout
бэк сразу ставит scan.paid = True и возвращает checkout_url=null.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_session
from ..deps import get_current_user
from ..models.scan import Scan, ScanStatus
from ..models.user import User
from ..plans import PAID_PLAN_ID, PLANS
from ..schemas.billing import CheckoutIn, CheckoutOut, PlanOut

router = APIRouter(prefix="/api/billing", tags=["billing"])


@router.get("/plans", response_model=list[PlanOut])
async def list_plans() -> list[PlanOut]:
    return [PlanOut(**p) for p in PLANS]


@router.post("/checkout", response_model=CheckoutOut)
async def create_checkout(
    body: CheckoutIn,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> CheckoutOut:
    if body.plan != PAID_PLAN_ID:
        raise HTTPException(status_code=400, detail="unknown plan")

    scan = await session.get(Scan, body.report_id)
    if scan is None or scan.user_id != user.id:
        raise HTTPException(status_code=404, detail="report not found")
    if scan.status != ScanStatus.done:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"report not ready (status={scan.status.value})",
        )

    # Dev-режим: помечаем отчёт оплаченным сразу. В проде это сделает webhook
    # CloudPayments после реальной оплаты.
    if not scan.paid:
        scan.paid = True
        await session.flush()

    return CheckoutOut(checkout_url=None, paid=True)
