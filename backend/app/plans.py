"""Каталог тарифов — единственный источник истины для бэка.

Фронт получает этот же список через GET /api/billing/plans (его дефолт во фронте
— только заглушка для MOCK-режима).
"""
from __future__ import annotations

from .models.user import UserPlan

PLANS: list[dict] = [
    {
        "id": "free",
        "name": "Бесплатно",
        "price": 0,
        "period": "",
        "highlight": False,
        "features": [
            "1 проверка сайта",
            "Риск-скоринг и нарушения",
            "Отчёт в браузере",
        ],
    },
    {
        "id": "pro",
        "name": "Pro",
        "price": 1490,
        "period": "/ мес",
        "highlight": True,
        "features": [
            "Безлимит проверок",
            "PDF-отчёты",
            "AI-анализ текстов политик",
            "История и повторные проверки",
            "Приоритеты для юриста/маркетолога/разработчика",
        ],
    },
    {
        "id": "team",
        "name": "Team",
        "price": 4900,
        "period": "/ мес",
        "highlight": False,
        "features": [
            "Всё из Pro",
            "До 10 пользователей",
            "Мониторинг сайтов по расписанию",
            "Экспорт и API-доступ",
        ],
    },
]


def is_paid(plan: UserPlan) -> bool:
    return plan in (UserPlan.pro, UserPlan.team)
