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


def processes_pii(crawl: dict) -> bool:
    """Публичная обёртка над _processes_pii (для llm_analyzer и т.п.)."""
    try:
        return _processes_pii(crawl)
    except Exception:  # noqa: BLE001
        return False


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
    # только если сайт обрабатывает ПДн (иначе он не оператор и идентифицировать
    # его 152-ФЗ не обязывает) — иначе ложное срабатывание на статичной визитке
    "no_operator_identification": lambda c: _processes_pii(c) and not (
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


def precondition_confirmed(violation_type: str, crawl: dict) -> bool:
    """СТРОГИЙ предикат для КОД-ГЕНЕРАЦИИ нарушений (detect_mechanical).

    В отличие от precondition_holds (мягкий ВАЛИДАТОР, fail-OPEN: на ошибке
    возвращает True, чтобы не выбросить присланное LLM), здесь семантика
    обратная — fail-CLOSED: нет предусловия или любая ошибка → False. Код
    НИКОГДА не выписывает нарушение без РЕАЛЬНО подтверждённого факта, иначе
    fail-open превратился бы в фабрикацию нарушений на кривом crawl."""
    if violation_type not in CATALOG:
        return False
    check = _PRECONDITIONS.get(violation_type)
    if check is None:
        return False  # нет признака для подтверждения → не выписываем
    try:
        return bool(check(crawl))
    except Exception:  # noqa: BLE001 — факт не подтверждён → не выписываем
        return False


# ─────────────────────────────────────────────────────────────────────────────
# Код-генерация МЕХАНИЧЕСКИХ нарушений (детерминизм).
#
# Тип «механический», если «есть/нет» определяется ЧИСТО булевым фактом из crawl,
# без суждения по тексту. Такие нарушения выписывает КОД (по тем же предусловиям
# выше), а не LLM — поэтому набор нарушений и сумма штрафов воспроизводимы между
# прогонами (LLM на одинаковом входе «дрожала»: то выписывала тип, то нет).
#
# «Судительные» типы (нужно читать текст документа или определять страну по IP)
# остаются за LLM — их код выписать не может без потери смысла.
# ─────────────────────────────────────────────────────────────────────────────

# Порядок фиксирован → стабильный порядок генерации (report_builder всё равно
# пересортирует по severity).
MECHANICAL: tuple[str, ...] = (
    "cross_border_transfer",
    "no_privacy_policy",
    "prechecked_consent",
    "tracking_before_consent",
    "form_without_consent",
    "no_operator_identification",
    "cookie_no_reject",
    "no_cookie_notice",
    "captcha_no_notice",
    # ВНИМАНИЕ: no_rkn_notification сюда НЕ входит сознательно. Его предусловие —
    # лишь "сайт обрабатывает ПДн", а факт самого нарушения (компания НЕ уведомила
    # РКН) краулер проверить не может — это внешний реестр, в crawl признака нет.
    # Выписывать его безусловно = ложное срабатывание + фиксированный штраф 300k
    # на каждом PII-сайте. Поэтому код его не генерирует; при необходимости его
    # стоит вынести в отдельный блок «проверьте вручную» БЕЗ суммы штрафа.
)

# Типы, требующие суждения LLM (по тексту документа / гео по IP).
JUDGMENT: tuple[str, ...] = (
    "server_outside_rf",
    "policy_incomplete",
    "consent_combined_with_ads",
    "no_subject_rights_info",
)

# Шаблоны описания/рекомендации для механических типов (детерминированная проза).
_MECH_TEXT: dict[str, tuple[str, str]] = {
    "cross_border_transfer": (
        "На сайте подключены зарубежные сервисы/трекеры, передающие данные "
        "посетителей за пределы РФ.",
        "Замените зарубежные сервисы на российские аналоги либо обеспечьте "
        "трансграничную передачу по требованиям ст. 12 152-ФЗ.",
    ),
    "no_privacy_policy": (
        "Сайт обрабатывает персональные данные (формы и/или трекеры), однако "
        "документ «Политика в отношении обработки персональных данных» не "
        "опубликован и ссылки на него отсутствуют.",
        "Разработайте и опубликуйте Политику обработки ПДн по ст. 18.1 152-ФЗ; "
        "разместите ссылку в подвале сайта и рядом с каждой формой сбора данных.",
    ),
    "prechecked_consent": (
        "Чекбокс согласия на обработку персональных данных проставлен по "
        "умолчанию — это не является добровольным и осознанным согласием.",
        "Снимите отметку с чекбокса согласия по умолчанию: пользователь должен "
        "проставить её сам перед отправкой формы.",
    ),
    "tracking_before_consent": (
        "Трекеры/аналитика срабатывают до получения согласия пользователя на "
        "обработку персональных данных.",
        "Откладывайте запуск трекеров до получения явного согласия пользователя.",
    ),
    "form_without_consent": (
        "На сайте присутствует форма сбора персональных данных без чекбокса "
        "получения согласия субъекта на их обработку.",
        "Добавьте в форму обязательный чекбокс с текстом согласия на обработку "
        "ПДн и ссылкой на политику конфиденциальности перед кнопкой отправки.",
    ),
    "no_operator_identification": (
        "В контактах и реквизитах сайта отсутствуют сведения о юридическом лице "
        "или ИП (наименование, ИНН, ОГРН), что не позволяет идентифицировать "
        "оператора персональных данных.",
        "Разместите в подвале сайта или разделе «Контакты» полное наименование "
        "юрлица (или ФИО ИП), ИНН и ОГРН.",
    ),
    "cookie_no_reject": (
        "На сайте есть cookie-баннер, но в нём отсутствует возможность отклонить "
        "необязательные файлы cookie.",
        "Добавьте в cookie-баннер кнопку «Отклонить» наравне с кнопкой согласия.",
    ),
    "no_cookie_notice": (
        "Сайт устанавливает cookie, однако баннер или уведомление об их "
        "использовании отсутствует.",
        "Реализуйте отображение баннера с уведомлением об использовании файлов "
        "cookie при первом посещении сайта.",
    ),
    "captcha_no_notice": (
        "На сайте используется captcha, обрабатывающая данные пользователя, без "
        "уведомления об этой обработке.",
        "Добавьте уведомление об обработке данных используемой captcha и ссылку "
        "на политику конфиденциальности.",
    ),
    "no_rkn_notification": (
        "Сайт обрабатывает персональные данные (через формы и/или трекеры), но "
        "признаков исполнения обязанности уведомить Роскомнадзор до начала "
        "обработки не обнаружено.",
        "Проверьте наличие компании в реестре операторов Роскомнадзора; при "
        "отсутствии записи подайте уведомление об обработке персональных данных.",
    ),
}


def _ev_trackers(crawl: dict, *, foreign_only: bool = False) -> str | None:
    tr = _summary(crawl).get("trackers") or []
    if foreign_only:
        tr = [t for t in tr if t.get("cross_border")]
    names = [str(t.get("name") or "?") for t in tr[:3]]
    return ("trackers: " + ", ".join(names)) if names else None


def _mech_evidence(violation_type: str, crawl: dict) -> list[str]:
    """Реальные факты из crawl под механическое нарушение (а не пересказ LLM)."""
    s = _summary(crawl)
    ev: list[str] = []
    t = violation_type

    if t == "cross_border_transfer":
        ev.append("has_cross_border_transfer: true" if s.get("has_cross_border_transfer")
                  else "обнаружены зарубежные трекеры")
        tr = _ev_trackers(crawl, foreign_only=True)
        if tr:
            ev.append(tr)
    elif t == "no_privacy_policy":
        ev.append("has_privacy_policy: false")
        if (s.get("forms_collecting_pii") or 0) > 0:
            ev.append(f"forms_collecting_pii: {s.get('forms_collecting_pii')}")
        tr = _ev_trackers(crawl)
        if tr:
            ev.append(tr)
    elif t == "prechecked_consent":
        n = s.get("forms_with_prechecked_consent") or 0
        ev.append(f"forms_with_prechecked_consent: {n}" if n else "pre_checked: true")
    elif t == "tracking_before_consent":
        ev.append("tracking_before_consent: true")
        tr = _ev_trackers(crawl)
        if tr:
            ev.append(tr)
    elif t == "form_without_consent":
        ev.append(f"forms_pii_without_consent: {s.get('forms_pii_without_consent') or 0}")
        kinds = s.get("pii_kinds_collected") or []
        if kinds:
            ev.append("pii_kinds_collected: " + ", ".join(str(k) for k in kinds[:6]))
    elif t == "no_operator_identification":
        ev += ["site_identity.inn: []", "site_identity.ogrn: []", "site_identity.legal_name_hints: []"]
    elif t == "cookie_no_reject":
        ev += ["has_cookie_banner: true", "cookie_banner_has_reject: false"]
    elif t == "no_cookie_notice":
        ev.append("has_cookie_banner: false")
        tr = _ev_trackers(crawl)
        if tr:
            ev.append(tr)
    elif t == "captcha_no_notice":
        ev.append("обнаружена captcha (trackers.category=captcha)")
    elif t == "no_rkn_notification":
        if (s.get("forms_collecting_pii") or 0) > 0:
            ev.append(f"forms_collecting_pii: {s.get('forms_collecting_pii')}")
        ev.append(f"trackers count: {len(s.get('trackers') or [])}")
    return ev[:5]


def detect_mechanical(crawl: dict) -> list[dict]:
    """Код-генерация механических нарушений по фактам crawl.

    Возвращает «сырые» нарушения (type/title/description/evidence/recommendation)
    в том же формате, что раньше присылала LLM — report_builder затем проставит
    severity/статью/штраф/роль из CATALOG и проверит предусловие (Fix A). Для
    механических типов предусловие здесь и есть критерий выписки.

    Используем СТРОГИЙ precondition_confirmed (fail-closed): факт не подтверждён
    или ошибка → нарушение НЕ выписываем (без фабрикации на кривом crawl)."""
    out: list[dict] = []
    for t in MECHANICAL:
        if not precondition_confirmed(t, crawl):
            continue
        spec = CATALOG[t]
        desc, rec = _MECH_TEXT.get(t, ("", ""))
        out.append({
            "type": t,
            "title": spec["title"],
            "description": desc,
            "evidence": _mech_evidence(t, crawl),
            "recommendation": rec,
        })
    return out


def passed_checks(crawl: dict, violations: list[dict]) -> list[dict]:
    """Детерминированные «пройденные проверки» по фактам crawl.

    Только то, что можно утверждать без суждения LLM (гео/локализацию не трогаем —
    она зависит от определения страны моделью)."""
    s = _summary(crawl)
    types = {v.get("type") for v in (violations or [])}
    out: list[dict] = []
    if (s.get("forms_total") or 0) > 0 and not _any_prechecked(crawl):
        out.append({
            "title": "Отсутствие предварительно отмеченных чекбоксов",
            "detail": "Формы не содержат чекбоксов согласия, установленных по умолчанию.",
        })
    if not _has_foreign_tracker(crawl) and "cross_border_transfer" not in types:
        out.append({
            "title": "Зарубежные трекеры не обнаружены",
            "detail": "Передача данных за пределы РФ через сторонние сервисы не выявлена.",
        })
    return out
