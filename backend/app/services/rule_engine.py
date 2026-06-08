"""Rule-engine: преобразует факты парсера (Контракт №1) в Контракт №2 для PDF/UI.

Парсер отдаёт факты (есть форма без согласия, баннер без кнопки отказа и т.п.).
Здесь мы превращаем факты в нарушения 152-ФЗ с привязкой к статьям, штрафам по
КоАП 13.11 и рекомендациями.

Скоринг — простой: старт 100, минус за нарушения по уровню severity. Это
осознанное упрощение MVP, который заказчик подтвердил.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

# Категории трекеров → русское название
_TRACKER_KIND_RU = {
    "analytics": "Аналитика",
    "tag_manager": "Менеджер тегов",
    "ad_pixel": "Рекламный пиксель",
    "session_replay": "Запись сессии",
    "crm_widget": "CRM-виджет",
    "chat_widget": "Чат-виджет",
    "captcha": "Captcha",
    "maps": "Карты",
    "social": "Соцсеть",
    "payment": "Платёжный виджет",
    "cdn": "CDN",
    "other": "Прочее",
}

# Штрафы по КоАП 13.11 (ориентировочно для юрлиц, MVP-таблица)
_FINES = {
    "consent_prechecked": 700_000,
    "no_localization": 1_000_000,
    "form_without_consent": 300_000,
    "third_party_undisclosed": 100_000,
    "cookie_no_reject": 100_000,
    "no_privacy_policy": 500_000,
    "no_https": 60_000,
    "cookie_banner_missing": 60_000,
    "captcha_notice_missing": 30_000,
}


def _score_penalty(severity: str) -> int:
    return {"critical": 25, "warning": 10, "info": 3}.get(severity, 0)


def _bucket(score: int) -> tuple[str, str]:
    """score → (risk_level, risk_label_ru)"""
    if score < 40:
        return "CRITICAL", "Критический риск"
    if score < 60:
        return "HIGH", "Высокий риск"
    if score < 80:
        return "MEDIUM", "Средний риск"
    if score < 95:
        return "LOW", "Низкий риск"
    return "SAFE", "Соответствует"


def build_report(crawl: dict[str, Any], *, report_id: uuid.UUID) -> dict[str, Any]:
    """Главная точка входа: факты парсера → JSON Контракта №2."""
    meta = crawl.get("meta", {}) or {}
    summary = crawl.get("summary", {}) or {}
    site_identity = crawl.get("site_identity", {}) or {}
    policy_documents = crawl.get("policy_documents", []) or []
    pages = crawl.get("pages", []) or []

    violations = _detect_violations(summary, pages, site_identity)

    # Скоринг
    score = 100 - sum(_score_penalty(v["severity"]) for v in violations)
    score = max(0, min(100, score))
    risk_level, risk_label = _bucket(score)

    # Технический скор: меньше веса юридическим вопросам, больше — формам/cookie
    tech_pen = sum(
        _score_penalty(v["severity"])
        for v in violations
        if v["target_role"] in ("developer", "marketer")
    )
    technical_score = max(0, min(100, 100 - tech_pen))
    # Юридический скор: акцент на политики/согласия
    legal_pen = sum(
        _score_penalty(v["severity"]) for v in violations if v["target_role"] == "lawyer"
    )
    legal_score = max(0, min(100, 100 - legal_pen))

    stats = {
        "critical_count": sum(1 for v in violations if v["severity"] == "critical"),
        "warning_count": sum(1 for v in violations if v["severity"] == "warning"),
        "info_count": sum(1 for v in violations if v["severity"] == "info"),
        "passed_count": 0,  # обновим ниже
    }

    passed_checks = _detect_passed(summary, site_identity, policy_documents)
    stats["passed_count"] = len(passed_checks)

    total_fine_rub = sum(int(v.get("fine_rub") or 0) for v in violations)

    verdict = _build_verdict(violations, risk_label)
    verdict_plain = _build_verdict_plain(violations)

    document_meta = {
        "report_id": str(report_id),
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "target_url": meta.get("requested_url") or meta.get("start_url") or "",
        "domain": meta.get("base_domain") or "",
        "organization_name": _first(site_identity.get("legal_name_hints", [])),
        "scan_duration_sec": (meta.get("duration_ms") or 0) / 1000.0 if meta.get("duration_ms") else None,
        "pages_scanned": meta.get("pages_crawled"),
        "scanner_version": meta.get("parser_version"),
    }

    infra = _build_infra(summary)

    technical_appendix = _build_appendix(summary, pages, policy_documents)

    return {
        "document_meta": document_meta,
        "scoring": {
            "overall_score": score,
            "risk_level": risk_level,
            "risk_label_ru": risk_label,
            "legal_score": legal_score,
            "technical_score": technical_score,
        },
        "executive_summary": {
            "verdict": verdict,
            "verdict_plain": verdict_plain,
            "stats": stats,
            "total_fine_rub": total_fine_rub,
            "passed_checks": passed_checks,
        },
        "infrastructure_and_geo": infra,
        "violations": violations,
        "technical_appendix": technical_appendix,
    }


# ──────────────────────────────────────────────────────────────────────────────
# Детекторы нарушений


def _detect_violations(summary: dict, pages: list, identity: dict) -> list[dict]:
    out: list[dict] = []
    counter = {"critical": 0, "warning": 0, "info": 0}

    def add(severity: str, prefix: str, **kw):
        counter[severity] += 1
        n = counter[severity]
        out.append({"id": f"{prefix}-{n:03d}", "severity": severity, **kw})

    # ст. 9 — согласие проставлено по умолчанию (pre-checked)
    if summary.get("forms_with_prechecked_consent", 0) > 0:
        evidence = []
        for p in pages:
            for f in p.get("forms", []) or []:
                for cb in f.get("consent_checkboxes", []) or []:
                    if cb.get("pre_checked"):
                        evidence.append(f"{p.get('url')} — чекбокс pre_checked=true: «{(cb.get('label') or '')[:120]}»")
        add(
            "critical", "ERR",
            article_152fz="ст. 9 (согласие)",
            title="Согласие на обработку ПДн проставлено по умолчанию",
            description=(
                "Найдены формы, в которых чекбокс согласия отмечен заранее (pre-checked). "
                "Согласие должно быть свободным, конкретным, информированным и однозначным."
            ),
            evidence=evidence[:5],
            target_role="developer",
            recommendation=(
                "Снять отметку с чекбокса по умолчанию. Согласие на обработку ПДн "
                "оформить отдельно от иных согласий (рассылки и т.п.)."
            ),
            fine_rub=_FINES["consent_prechecked"],
        )

    # ст. 9 — форма ПДн без чекбокса согласия
    if summary.get("forms_pii_without_consent", 0) > 0:
        evidence = []
        for p in pages:
            for f in p.get("forms", []) or []:
                if f.get("pii_kinds") and not f.get("consent_checkboxes"):
                    evidence.append(f"{p.get('url')} — форма {f.get('action') or '(без action)'} собирает ПДн без согласия")
        add(
            "warning", "WARN",
            article_152fz="ст. 9 (согласие)",
            title="Форма сбора ПДн без чекбокса согласия",
            description="Найдены формы, собирающие персональные данные, без отдельного чекбокса согласия.",
            evidence=evidence[:5],
            target_role="lawyer",
            recommendation=(
                "Добавить во все формы сбора ПДн чекбокс согласия со ссылкой на политику; "
                "без отметки отправка формы должна блокироваться."
            ),
            fine_rub=_FINES["form_without_consent"],
        )

    # ст. 18 ч. 5 — локализация (есть передача данных за рубеж)
    if summary.get("has_cross_border_transfer"):
        foreign = [
            t["name"] for t in (summary.get("trackers") or []) if t.get("cross_border")
        ]
        add(
            "critical", "ERR",
            article_152fz="ст. 18 ч. 5 (локализация)",
            title="Обработка ПДн граждан РФ вне территории России",
            description=(
                "Найдены сторонние сервисы, передающие данные за рубеж. Это создаёт риск "
                "нарушения требования о локализации баз данных граждан РФ."
            ),
            evidence=[f"Трекер с трансграничной передачей: {n}" for n in foreign[:5]],
            target_role="developer",
            recommendation=(
                "Перенести хранение и первичную обработку ПДн граждан РФ в базы данных на территории РФ. "
                "При использовании сторонних сервисов убедиться, что ПДн не покидают РФ."
            ),
            fine_rub=_FINES["no_localization"],
        )

    # ст. 7, 6 — передача третьим лицам без явного раскрытия
    if (summary.get("third_party_domain_count") or 0) > 0:
        domains = (summary.get("third_party_domains") or [])[:5]
        add(
            "warning", "WARN",
            article_152fz="ст. 7, ст. 6 (передача третьим лицам)",
            title="Передача данных третьим лицам",
            description=(
                "Сайт обращается к сторонним сервисам (аналитика, виджеты, CDN). "
                "Это передача данных третьим лицам и требует явного раскрытия в политике."
            ),
            evidence=[f"Сторонний домен: {d}" for d in domains],
            target_role="lawyer",
            recommendation=(
                "Перечислить в политике конфиденциальности всех получателей данных, цели и правовые "
                "основания передачи. Обновить cookie-баннер: явно указать передачу данных третьим лицам."
            ),
            fine_rub=_FINES["third_party_undisclosed"],
        )

    # cookie-баннер без кнопки отказа
    if summary.get("has_cookie_banner") and not summary.get("cookie_banner_has_reject"):
        add(
            "warning", "WARN",
            article_152fz="ст. 9 (информированность)",
            title="Cookie-баннер без кнопки отказа",
            description="Cookie-баннер не даёт пользователю отклонить необязательные cookie — есть только кнопка «Принять».",
            evidence=["Найден баннер с has_reject_button=false"],
            target_role="marketer",
            recommendation=(
                "Добавить в баннер кнопку отказа и/или настройки cookie, чтобы пользователь мог отклонить "
                "необязательные трекеры до их загрузки."
            ),
            fine_rub=_FINES["cookie_no_reject"],
        )

    # трекеры до согласия
    if summary.get("tracking_before_consent"):
        add(
            "critical", "ERR",
            article_152fz="ст. 9 (согласие)",
            title="Трекеры срабатывают до согласия",
            description=(
                "На страницах сайта обнаружены активные сторонние трекеры/cookie ДО получения согласия "
                "пользователя через cookie-баннер."
            ),
            evidence=["tracking_before_consent=true"],
            target_role="developer",
            recommendation=(
                "Загружать неосновные трекеры только после явного согласия пользователя. "
                "До согласия — никаких сторонних cookie и пикселей."
            ),
            fine_rub=_FINES["consent_prechecked"],
        )

    # политика конфиденциальности отсутствует
    if not summary.get("has_privacy_policy"):
        add(
            "critical", "ERR",
            article_152fz="ст. 18.1 (политика оператора)",
            title="Политика обработки ПДн не найдена",
            description="На сайте не обнаружено ссылки на политику обработки персональных данных.",
            evidence=["has_privacy_policy=false"],
            target_role="lawyer",
            recommendation=(
                "Разместить документ «Политика обработки персональных данных» в открытом доступе "
                "и сослаться на него с главной/футера и из всех форм сбора ПДн."
            ),
            fine_rub=_FINES["no_privacy_policy"],
        )

    # cookie-баннер вообще отсутствует
    if not summary.get("has_cookie_banner"):
        add(
            "info", "INFO",
            article_152fz="ст. 9 (информированность)",
            title="Cookie-уведомление не найдено",
            description="На сайте не найдено информирующего баннера об использовании cookie.",
            evidence=["has_cookie_banner=false"],
            target_role="marketer",
            recommendation="Добавить cookie-баннер с кнопками «принять» и «отклонить».",
            fine_rub=_FINES["cookie_banner_missing"],
        )

    # captcha без уведомления (требование заказчика — должны информировать)
    has_captcha = any(
        (t.get("category") == "captcha") for t in (summary.get("trackers") or [])
    )
    if has_captcha:
        add(
            "info", "INFO",
            article_152fz="ст. 9 (информированность)",
            title="Используется captcha без явного уведомления",
            description=(
                "Сайт использует captcha. Если captcha сторонняя, она собирает технические данные "
                "пользователя — это должно быть раскрыто пользователю."
            ),
            evidence=["Найден трекер категории captcha"],
            target_role="lawyer",
            recommendation="Добавить уведомление об использовании captcha рядом с формами или в политике.",
            fine_rub=_FINES["captcha_notice_missing"],
        )

    # оператор не идентифицирован
    if not (identity.get("legal_name_hints") or identity.get("inn") or identity.get("ogrn")):
        add(
            "warning", "WARN",
            article_152fz="ст. 18.1 (оператор)",
            title="Оператор ПДн не идентифицирован",
            description="На сайте не удалось найти реквизиты оператора (название юрлица, ИНН/ОГРН).",
            evidence=["site_identity без legal_name_hints/inn/ogrn"],
            target_role="lawyer",
            recommendation="Указать в футере/контактах полное наименование оператора, ИНН и ОГРН.",
            fine_rub=_FINES["no_privacy_policy"] // 5,
        )

    return out


def _detect_passed(summary: dict, identity: dict, policies: list) -> list[dict]:
    out = []
    if summary.get("has_privacy_policy"):
        urls = summary.get("privacy_policy_urls") or []
        out.append({
            "title": "Политика конфиденциальности найдена и доступна",
            "detail": f"Документ опубликован: {urls[0]}" if urls else None,
        })
    if summary.get("has_cookie_banner") and summary.get("cookie_banner_has_reject"):
        out.append({
            "title": "Cookie-баннер с возможностью отказа",
            "detail": "Пользователь может отклонить необязательные cookie.",
        })
    if identity.get("legal_name_hints"):
        out.append({
            "title": "Указан оператор обработки персональных данных",
            "detail": f"В реквизитах назван оператор: {identity['legal_name_hints'][0]}",
        })
    if identity.get("contact_emails"):
        out.append({
            "title": "Указан контакт для обращений субъекта ПДн",
            "detail": f"Email: {identity['contact_emails'][0]}",
        })
    if any((p.get("kind") == "consent" and p.get("fetch_status") == 200) for p in policies):
        out.append({
            "title": "Найден документ «Согласие на обработку ПДн»",
            "detail": None,
        })
    return out


def _build_infra(summary: dict) -> dict:
    """В Контракте №1 у нас нет server_ip — вычисляем риск только по cross-border."""
    cross = bool(summary.get("has_cross_border_transfer"))
    return {
        "server_ip": None,
        "server_country": None,
        "server_country_ru": None,
        "hosting_provider": None,
        "localization_compliant": not cross,
        "localization_note": (
            "Сайт обращается к зарубежным сервисам — есть риск нарушения ст. 18 ч. 5 (локализация ПДн)."
            if cross
            else "Признаков трансграничной передачи данных не обнаружено."
        ),
    }


def _build_appendix(summary: dict, pages: list, policies: list) -> dict:
    # документы
    docs_map = {
        "privacy_policy": "Политика конфиденциальности",
        "consent": "Согласие на обработку ПДн",
        "cookie_policy": "Политика в отношении cookie",
        "terms": "Пользовательское соглашение",
    }
    found_kinds = {p.get("kind"): p for p in policies}
    documents_found = []
    for kind, name in docs_map.items():
        p = found_kinds.get(kind)
        documents_found.append({
            "name": name,
            "url": (p or {}).get("url"),
            "status": "Найдена и проанализирована" if p else "Не найдена",
        })

    # трекеры
    trackers = summary.get("trackers") or []
    items = []
    for t in trackers:
        items.append({
            "name": t.get("name"),
            "host": (t.get("found_on") or [None])[0],
            "origin": "foreign" if t.get("cross_border") else "ru",
            "kind": _TRACKER_KIND_RU.get(t.get("category"), t.get("category")),
        })
    trackers_summary = {
        "total": len(items),
        "russian": sum(1 for i in items if i["origin"] == "ru"),
        "foreign": sum(1 for i in items if i["origin"] == "foreign"),
        "list": items,
    }

    # точки сбора данных
    points = []
    for p in pages:
        for f in p.get("forms", []) or []:
            if not f.get("pii_kinds"):
                continue
            points.append({
                "url": p.get("url"),
                "form_name": f.get("action") or None,
                "fields": [fld.get("name") for fld in (f.get("fields") or []) if fld.get("name")],
            })

    return {
        "documents_found": documents_found,
        "trackers_summary": trackers_summary,
        "data_collection_points": points,
        "ai_analysis": [],  # заполняется LLM-сервисом (опционально, paid-tier)
    }


def _build_verdict(violations: list, risk_label: str) -> str:
    if not violations:
        return "Существенных нарушений 152-ФЗ не выявлено. Рекомендуем поддерживать текущую конфигурацию."
    crit = [v["title"] for v in violations if v["severity"] == "critical"]
    parts = [f"Уровень риска: {risk_label.lower()}."]
    if crit:
        parts.append("Критичные нарушения: " + "; ".join(crit) + ".")
    parts.append("Подробности и рекомендации — в разделе «Нарушения».")
    return " ".join(parts)


def _build_verdict_plain(violations: list) -> str:
    if not violations:
        return "На сайте всё чисто — крупных проблем с 152-ФЗ не нашли."
    n_crit = sum(1 for v in violations if v["severity"] == "critical")
    if n_crit:
        return (
            f"Нашли {n_crit} критичных проблем, которые могут привести к штрафу. "
            "Их стоит починить в первую очередь."
        )
    return "Серьёзных проблем нет, но есть мелкие замечания — посмотрите список нарушений."


def _first(seq):
    return seq[0] if seq else None
