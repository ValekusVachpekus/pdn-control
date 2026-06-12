"""Каталог нарушений 152-ФЗ — детерминированная таблица квалификации.

Гибридный подход: LLM ДЕТЕКТИРУЕТ факт нарушения (какой тип присутствует) и
описывает его конкретику (evidence, description, recommendation по тексту
сайта). Но severity, статья, штраф и target_role берутся ИЗ ЭТОЙ ТАБЛИЦЫ, а не
из усмотрения модели. Это убирает дрожание оценки и делает штрафы
воспроизводимыми и юридически защитимыми.

Штрафы — потолки для ЮРИДИЧЕСКИХ ЛИЦ по КоАП РФ ст. 13.11 (ред. с 30.05.2025):
    ч. 1   обработка без оснований / не по целям      → 300 000
    ч. 2   без согласия / нарушение формы согласия     → 700 000
    ч. 3   не опубликована политика оператора          →  60 000
    ч. 4   не предоставил субъекту информацию          →  80 000
    ч. 5   не выполнил требование субъекта             →  90 000
    ч. 8   нет локализации БД ПДн на территории РФ     → 6 000 000
    ч. 10  не уведомил РКН о намерении обрабатывать    → 300 000

⚠️ Таблицу перед продакшеном ДОЛЖЕН проверить юрист — это самая юридически
чувствительная часть продукта.
"""
from __future__ import annotations

from typing import TypedDict


class ViolationSpec(TypedDict):
    article_152fz: str
    severity: str       # critical | warning | info
    fine_rub: int       # потолок штрафа для ЮЛ по КоАП 13.11
    target_role: str    # developer | lawyer | marketer
    title: str          # дефолтный заголовок (LLM может уточнить под сайт)


# Ключ — стабильный код типа нарушения. LLM возвращает именно этот код в поле
# "type". Если кода нет в каталоге — нарушение отбрасывается (см. report_builder).
CATALOG: dict[str, ViolationSpec] = {
    # ── Локализация (самые крупные штрафы) ──────────────────────────────────
    "cross_border_transfer": {
        "article_152fz": "ст. 18 ч. 5",
        "severity": "critical",
        "fine_rub": 6_000_000,
        "target_role": "developer",
        "title": "Трансграничная передача ПДн через зарубежные сервисы",
    },
    "server_outside_rf": {
        "article_152fz": "ст. 18 ч. 5",
        "severity": "critical",
        "fine_rub": 6_000_000,
        "target_role": "developer",
        "title": "Сервер с ПДн расположен за пределами РФ",
    },

    # ── Согласие (ст. 9, штрафы по КоАП ч. 2) ────────────────────────────────
    "prechecked_consent": {
        "article_152fz": "ст. 9 ч. 1",
        "severity": "critical",
        "fine_rub": 700_000,
        "target_role": "developer",
        "title": "Согласие на обработку ПДн проставлено по умолчанию",
    },
    "form_without_consent": {
        "article_152fz": "ст. 9 ч. 1",
        "severity": "warning",
        "fine_rub": 700_000,
        "target_role": "developer",
        "title": "Форма сбора ПДн без согласия пользователя",
    },
    "tracking_before_consent": {
        "article_152fz": "ст. 9 ч. 1",
        "severity": "critical",
        "fine_rub": 700_000,
        "target_role": "developer",
        "title": "Трекеры срабатывают до получения согласия",
    },
    "consent_combined_with_ads": {
        "article_152fz": "ст. 9 ч. 1",
        "severity": "warning",
        "fine_rub": 700_000,
        "target_role": "lawyer",
        "title": "Согласие на ПДн совмещено с согласием на рекламу",
    },

    # ── Политика оператора (ст. 18.1, штрафы по КоАП ч. 3) ───────────────────
    "no_privacy_policy": {
        "article_152fz": "ст. 18.1 ч. 2",
        "severity": "critical",
        "fine_rub": 60_000,
        "target_role": "lawyer",
        "title": "Политика обработки ПДн не опубликована",
    },
    "policy_incomplete": {
        "article_152fz": "ст. 18.1 ч. 2",
        "severity": "warning",
        "fine_rub": 60_000,
        "target_role": "lawyer",
        "title": "Политика конфиденциальности неполная",
    },
    "no_operator_identification": {
        "article_152fz": "ст. 18.1",
        "severity": "warning",
        "fine_rub": 60_000,
        "target_role": "lawyer",
        "title": "Оператор ПДн не идентифицирован",
    },

    # ── Cookie / информирование ─────────────────────────────────────────────
    "cookie_no_reject": {
        "article_152fz": "ст. 18.1 ч. 2",
        "severity": "warning",
        "fine_rub": 60_000,
        "target_role": "marketer",
        "title": "Cookie-баннер без возможности отказа",
    },
    "no_cookie_notice": {
        "article_152fz": "ст. 18.1 ч. 2",
        "severity": "info",
        "fine_rub": 60_000,
        "target_role": "marketer",
        "title": "Cookie-уведомление отсутствует",
    },
    "captcha_no_notice": {
        "article_152fz": "ст. 9 ч. 1",
        "severity": "info",
        "fine_rub": 60_000,
        "target_role": "lawyer",
        "title": "Используется captcha без уведомления",
    },

    # ── Уведомление Роскомнадзора (КоАП ч. 10) ──────────────────────────────
    "no_rkn_notification": {
        "article_152fz": "ст. 22 ч. 1",
        "severity": "info",
        "fine_rub": 300_000,
        "target_role": "lawyer",
        "title": "Роскомнадзор не уведомлён об обработке ПДн",
    },

    # ── Права субъекта (КоАП ч. 4-5) ────────────────────────────────────────
    "no_subject_rights_info": {
        "article_152fz": "ст. 14",
        "severity": "warning",
        "fine_rub": 80_000,
        "target_role": "lawyer",
        "title": "Не раскрыт порядок реализации прав субъекта ПДн",
    },
}

# Список кодов для подстановки в промпт LLM (чтобы модель знала допустимые типы).
KNOWN_TYPES = tuple(CATALOG.keys())


def spec_for(violation_type: str) -> ViolationSpec | None:
    """Вернёт квалификацию по типу или None, если тип неизвестен."""
    return CATALOG.get(violation_type)
