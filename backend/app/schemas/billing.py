"""Pydantic-схемы для эндпоинтов биллинга."""
from __future__ import annotations

from pydantic import BaseModel


class PlanOut(BaseModel):
    id: str
    name: str
    price: int
    period: str
    highlight: bool
    features: list[str]


class CheckoutIn(BaseModel):
    plan: str


class CheckoutOut(BaseModel):
    checkout_url: str | None
