"""GET /api/billing/plans — каталог тарифов;
POST /api/billing/checkout — заглушка под платёжного провайдера.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from ..deps import get_current_user
from ..models.user import User
from ..plans import PLANS
from ..schemas.billing import CheckoutIn, CheckoutOut, PlanOut

router = APIRouter(prefix="/api/billing", tags=["billing"])


@router.get("/plans", response_model=list[PlanOut])
async def list_plans() -> list[PlanOut]:
    return [PlanOut(**p) for p in PLANS]


@router.post("/checkout", response_model=CheckoutOut)
async def create_checkout(
    body: CheckoutIn,
    user: User = Depends(get_current_user),
) -> CheckoutOut:
    valid_ids = {p["id"] for p in PLANS}
    if body.plan not in valid_ids:
        raise HTTPException(status_code=400, detail="unknown plan")
    if body.plan == "free":
        raise HTTPException(status_code=400, detail="free plan does not need checkout")

    # MVP: интеграции с провайдером нет — возвращаем null, фронт покажет «скоро».
    return CheckoutOut(checkout_url=None)
