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


# ─────────────────────────────────────────────────────────────────────────────
# Фикс A — предусловия (анти-галлюцинация).
#
# Для каждого типа нарушения задано булево условие над фактами crawl. Код —
# ВАЛИДАТОР, а не генератор: он НИКОГДА не выписывает нарушение сам, но если LLM
# выписала нарушение, под которым в crawl НЕТ факта — отбрасывает его как
# выдумку. Контекстное «является ли это нарушением» остаётся за LLM; код лишь
# не даёт соврать про факт.
#
# Типы делятся на:
#   • механические — факт проверяется напрямую по флагам summary/site_identity;
#   • текстовые (policy_incomplete и т.п.) — код проверяет лишь, что текст для
#     суждения вообще существует (нельзя «политика неполная» при отсутствии
#     политики), но само суждение о полноте оставляет LLM.
# ─────────────────────────────────────────────────────────────────────────────


def _summary(crawl: dict) -> dict:
    return crawl.get("summary", {}) or {}


def _identity(crawl: dict) -> dict:
    return crawl.get("site_identity", {}) or {}


def _has_foreign_tracker(crawl: dict) -> bool:
    return any(t.get("cross_border") for t in (_summary(crawl).get("trackers") or []))


def _processes_pii(crawl: dict) -> bool:
    """Сайт обрабатывает ПДн: есть трекеры/сторонние домены или формы с PII."""
    s = _summary(crawl)
    return (
        bool(s.get("trackers"))
        or (s.get("third_party_domain_count") or 0) > 0
        or (s.get("forms_collecting_pii") or 0) > 0
        or (s.get("forms_total") or 0) > 0
    )


def _any_prechecked(crawl: dict) -> bool:
    for p in crawl.get("pages", []) or []:
        for f in p.get("forms", []) or []:
            for cb in f.get("consent_checkboxes", []) or []:
                if cb.get("pre_checked"):
                    return True
    return False


def _has_consent_text(crawl: dict) -> bool:
    for p in crawl.get("pages", []) or []:
        for f in p.get("forms", []) or []:
            for cb in f.get("consent_checkboxes", []) or []:
                if (cb.get("full_text") or cb.get("label") or "").strip():
                    return True
    return False


def _has_policy_text(crawl: dict) -> bool:
    for d in crawl.get("policy_documents", []) or []:
        if d.get("kind") == "privacy_policy" and (d.get("extracted_text") or "").strip():
            return True
    return False


# type → callable(crawl) -> bool. True = факт под нарушением подтверждён.
_PRECONDITIONS = {
    "cross_border_transfer": lambda c: bool(_summary(c).get("has_cross_border_transfer")) or _has_foreign_tracker(c),
    # страну по IP определяет LLM; код требует лишь наличие IP (без него вывод невозможен)
    "server_outside_rf": lambda c: bool((c.get("meta", {}) or {}).get("server_ip")),
    "prechecked_consent": lambda c: (_summary(c).get("forms_with_prechecked_consent") or 0) > 0 or _any_prechecked(c),
    "form_without_consent": lambda c: (_summary(c).get("forms_pii_without_consent") or 0) > 0,
    "tracking_before_consent": lambda c: bool(_summary(c).get("tracking_before_consent")),
    # текстовый: нужен хотя бы текст согласия, чтобы судить о совмещении с рекламой
    "consent_combined_with_ads": lambda c: _has_consent_text(c),
    "no_privacy_policy": lambda c: not _summary(c).get("has_privacy_policy") and _processes_pii(c),
    # текстовый: «политика неполная» имеет смысл только если политика есть
    "policy_incomplete": lambda c: bool(_summary(c).get("has_privacy_policy")) and _has_policy_text(c),
    "no_operator_identification": lambda c: not (
        _identity(c).get("inn") or _identity(c).get("ogrn") or _identity(c).get("legal_name_hints")
    ),
    "cookie_no_reject": lambda c: bool(_summary(c).get("has_cookie_banner")) and not _summary(c).get("cookie_banner_has_reject"),
    "no_cookie_notice": lambda c: not _summary(c).get("has_cookie_banner") and _processes_pii(c),
    "captcha_no_notice": lambda c: any(t.get("category") == "captcha" for t in (_summary(c).get("trackers") or [])),
    # обязанность уведомить РКН возникает только если сайт обрабатывает ПДн
    "no_rkn_notification": lambda c: _processes_pii(c),
    # текстовый: нужно наличие политики, чтобы судить о раскрытии прав субъекта
    "no_subject_rights_info": lambda c: _has_policy_text(c),
}


def precondition_holds(violation_type: str, crawl: dict) -> bool:
    """True, если факт под нарушением подтверждается crawl-данными.

    Неизвестный тип → False (его и так отбросят как вне каталога). Тип без
    предусловия → True (не отбрасываем, страховка на случай расширения)."""
    if violation_type not in CATALOG:
        return False
    check = _PRECONDITIONS.get(violation_type)
    if check is None:
        return True
    try:
        return bool(check(crawl))
    except Exception:  # noqa: BLE001 — на кривом crawl не валим весь отчёт
        return True
