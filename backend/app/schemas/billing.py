"""Pydantic-схемы для эндпоинтов биллинга (разовая оплата за отчёт)."""
from __future__ import annotations

import uuid

from pydantic import BaseModel, Field


class PlanOut(BaseModel):
    id: str
    name: str
    price: int
    period: str
    highlight: bool
    features: list[str]


class CheckoutIn(BaseModel):
    plan: str = Field(..., description="id продукта (сейчас всегда 'paid')")
    report_id: uuid.UUID = Field(..., description="ID отчёта, который разблокируется после оплаты")


class CheckoutOut(BaseModel):
    # URL виджета/страницы CloudPayments. None — пока реальная интеграция не
    # подключена; в dev-режиме бэк сам помечает отчёт оплаченным.
    checkout_url: str | None
    # paid=True означает, что в dev-режиме бэк уже зафиксировал оплату — фронт
    # может сразу перейти к показу полного отчёта.
    paid: bool
