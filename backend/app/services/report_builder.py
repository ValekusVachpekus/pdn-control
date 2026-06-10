"""Сборка итогового Контракта №2 из (CrawlJSON + LLM-ответ).

Чёткое разделение:
  - АЛГОРИТМ берёт из crawl: document_meta, перечень найденных документов,
    список трекеров с категориями, точки сбора данных (формы с PII), сырой IP/
    страну сервера (если парсер их извлёк).
  - LLM возвращает: violations[], scoring, executive_summary, passed_checks,
    infrastructure_and_geo.localization_*, ai_analysis[].

Алгоритм НЕ выносит юр-вердиктов. Если что-то отсутствует в LLM-ответе —
подставляем безопасные дефолты (пустой список, None и т.п.), но не выдумываем.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

# Категории трекеров → русское название (для technical_appendix.trackers_summary.list[].kind)
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


def _document_meta(crawl: dict, report_id: uuid.UUID) -> dict:
    meta = crawl.get("meta", {}) or {}
    site_identity = crawl.get("site_identity", {}) or {}
    duration_ms = meta.get("duration_ms")
    return {
        "report_id": str(report_id),
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "target_url": meta.get("requested_url") or meta.get("start_url") or "",
        "domain": meta.get("base_domain") or "",
        # Берём первый найденный признак юр.лица — это просто факт из футера.
        "organization_name": (site_identity.get("legal_name_hints") or [None])[0],
        "scan_duration_sec": duration_ms / 1000.0 if duration_ms else None,
        "pages_scanned": meta.get("pages_crawled"),
        "scanner_version": meta.get("parser_version"),
    }


def _documents_found(crawl: dict) -> list[dict]:
    """Какие политики/согласия нашёл парсер. Это просто факт."""
    label = {
        "privacy_policy": "Политика конфиденциальности",
        "consent": "Согласие на обработку ПДн",
        "cookie_policy": "Политика в отношении cookie",
        "terms": "Пользовательское соглашение",
    }
    found_by_kind = {d.get("kind"): d for d in (crawl.get("policy_documents", []) or [])}
    out: list[dict] = []
    for kind, name in label.items():
        doc = found_by_kind.get(kind)
        out.append({
            "name": name,
            "url": (doc or {}).get("url"),
            "status": "Найдена и проанализирована" if doc else "Не найдена",
        })
    return out


def _trackers_summary(crawl: dict) -> dict:
    trackers = (crawl.get("summary", {}) or {}).get("trackers") or []
    items = []
    for t in trackers:
        items.append({
            "name": t.get("name"),
            "host": (t.get("found_on") or [None])[0],
            "origin": "foreign" if t.get("cross_border") else "ru",
            "kind": _TRACKER_KIND_RU.get(t.get("category"), t.get("category")),
        })
    return {
        "total": len(items),
        "russian": sum(1 for i in items if i["origin"] == "ru"),
        "foreign": sum(1 for i in items if i["origin"] == "foreign"),
        "list": items,
    }


def _data_collection_points(crawl: dict) -> list[dict]:
    """Формы со сборкой PII. Алгоритм просто перечисляет, без оценок."""
    points: list[dict] = []
    for page in crawl.get("pages", []) or []:
        for f in page.get("forms", []) or []:
            if not f.get("pii_kinds"):
                continue
            points.append({
                "url": page.get("url"),
                "form_name": f.get("action") or None,
                "fields": [
                    fld.get("name")
                    for fld in (f.get("fields") or [])
                    if fld.get("name")
                ],
            })
    return points


def _empty_report(crawl: dict, report_id: uuid.UUID) -> dict:
    """Парсер не получил ни одной страницы — отдаём честный «не проверено».

    Сюда мы не зовём LLM (нечего анализировать). Алгоритм просто формирует
    заглушку — без юр-вердиктов.
    """
    meta = crawl.get("meta", {}) or {}
    errors = meta.get("errors") or []
    err_text = "; ".join(str(e) for e in errors[:3]) if errors else None
    verdict = (
        "Не удалось получить страницы сайта: возможно, сайт защищён captcha/бот-детектором, "
        "временно недоступен или требует JS-рендера, недоступного парсеру. "
        "Попробуйте повторить проверку позже."
    )
    return {
        "document_meta": _document_meta(crawl, report_id),
        "scoring": {
            "overall_score": None,
            "risk_level": "UNKNOWN",
            "risk_label_ru": "Не проверено",
            "legal_score": None,
            "technical_score": None,
        },
        "executive_summary": {
            "verdict": verdict + (f" Технические ошибки: {err_text}." if err_text else ""),
            "verdict_plain": verdict,
            "stats": {"critical_count": 0, "warning_count": 0, "info_count": 0, "passed_count": 0},
            "total_fine_rub": 0,
            "passed_checks": [],
        },
        "infrastructure_and_geo": {
            "server_ip": None, "server_country": None, "server_country_ru": None,
            "hosting_provider": None,
            "localization_compliant": False, "localization_status": "unknown",
            "localization_note": "Данные не получены — сайт не удалось обойти.",
        },
        "violations": [],
        "technical_appendix": {
            "documents_found": [], "trackers_summary": {"total": 0, "russian": 0, "foreign": 0, "list": []},
            "data_collection_points": [], "ai_analysis": [],
        },
        "_scan_failed": True,
        # маркер источника: LLM не вызывался
        "_ai_powered": False,
    }


_ID_PREFIX = {"critical": "ERR", "warning": "WARN", "info": "INFO"}


def _normalize_violations(raw: Any) -> list[dict]:
    """Достаём violations[] из LLM-ответа, отбрасываем мусор, заполняем дефолты.

    LLM регулярно путает префиксы id (выписывает «ERR-003» для warning, и т.п.).
    Поэтому id'ы перенумеровываем сами по строгой схеме: ERR-001..ERR-N для
    critical, WARN-001..WARN-N для warning, INFO-001..INFO-N для info — в том
    порядке, в котором LLM их выдал внутри своей группы severity.
    """
    if not isinstance(raw, list):
        return []
    out: list[dict] = []
    for v in raw:
        if not isinstance(v, dict):
            continue
        severity = v.get("severity")
        if severity not in ("critical", "warning", "info"):
            continue
        title = (v.get("title") or "").strip()
        description = (v.get("description") or "").strip()
        if not title or not description:
            continue
        out.append({
            "id": "",  # проставим ниже после сортировки по severity
            "severity": severity,
            "article_152fz": (v.get("article_152fz") or "").strip()[:60],
            "title": title[:200],
            "description": description[:800],
            "evidence": [str(e)[:300] for e in (v.get("evidence") or []) if str(e).strip()][:5],
            "target_role": v.get("target_role") if v.get("target_role") in
                ("developer", "lawyer", "marketer") else "lawyer",
            "recommendation": (v.get("recommendation") or "").strip()[:800],
            "fine_rub": int(v.get("fine_rub") or 0) if isinstance(v.get("fine_rub"), (int, float)) else 0,
        })

    # Перенумерация id'ов: считаем номер внутри каждой группы severity.
    counters: dict[str, int] = {"critical": 0, "warning": 0, "info": 0}
    for v in out:
        counters[v["severity"]] += 1
        v["id"] = f"{_ID_PREFIX[v['severity']]}-{counters[v['severity']]:03d}"
    return out


_SEVERITY_PENALTY = {"critical": 25, "warning": 10, "info": 3}


def _compute_score(violations: list[dict], roles: tuple[str, ...] | None = None) -> int:
    """100 − Σ(penalty по severity). LLM в промпте инструктирован считать так же,
    но на практике «смягчает» оценку — пересчитываем сами, чтобы скоринг был
    воспроизводим: одни и те же violations → один и тот же балл."""
    penalty = sum(
        _SEVERITY_PENALTY.get(v.get("severity"), 0)
        for v in violations
        if roles is None or v.get("target_role") in roles
    )
    return max(0, min(100, 100 - penalty))


def _risk_band(score: int) -> tuple[str, str]:
    """Один источник истины для перевода балла в уровень риска."""
    if score < 40:
        return "CRITICAL", "Критический риск"
    if score < 60:
        return "HIGH", "Высокий риск"
    if score < 80:
        return "MEDIUM", "Средний риск"
    if score < 95:
        return "LOW", "Низкий риск"
    return "SAFE", "Соответствует"


def _normalize_scoring(raw: Any, violations: list[dict]) -> dict:
    """LLM-овский scoring используем только как hint; источник истины — формула."""
    raw = raw if isinstance(raw, dict) else {}
    overall = _compute_score(violations)
    legal = _compute_score(violations, roles=("lawyer",))
    technical = _compute_score(violations, roles=("developer", "marketer"))
    risk_level, risk_label = _risk_band(overall)
    return {
        "overall_score": overall,
        "risk_level": risk_level,
        "risk_label_ru": risk_label,
        "legal_score": legal,
        "technical_score": technical,
    }


def _normalize_executive(raw: Any, fallback_verdict: str = "") -> dict:
    raw = raw if isinstance(raw, dict) else {}
    return {
        "verdict": (raw.get("verdict") or fallback_verdict).strip()[:2000],
        "verdict_plain": (raw.get("verdict_plain") or raw.get("verdict") or fallback_verdict).strip()[:1500],
    }


def _normalize_passed_checks(raw: Any) -> list[dict]:
    if not isinstance(raw, list):
        return []
    out: list[dict] = []
    for p in raw:
        if not isinstance(p, dict):
            continue
        title = (p.get("title") or "").strip()
        if not title:
            continue
        out.append({"title": title[:200], "detail": (p.get("detail") or "").strip()[:400] or None})
    return out


def _normalize_infra(raw: Any, crawl: dict) -> dict:
    """server_ip берём из crawl.meta (его кладёт парсер).
    server_country, server_country_ru, hosting_provider и localization_* —
    выводит LLM по этому IP (см. промпт в llm_analyzer.py).
    """
    raw = raw if isinstance(raw, dict) else {}
    meta = crawl.get("meta", {}) or {}
    status = raw.get("localization_status")
    if status not in ("compliant", "non_compliant", "unknown"):
        status = "unknown"
    return {
        "server_ip": meta.get("server_ip"),
        "server_country": (raw.get("server_country") or "").strip()[:8] or None,
        "server_country_ru": (raw.get("server_country_ru") or "").strip()[:60] or None,
        "hosting_provider": (raw.get("hosting_provider") or "").strip()[:120] or None,
        # legacy bool для PDF-шаблонов, не знающих про tri-state
        "localization_compliant": (status == "compliant"),
        "localization_status": status,
        "localization_note": (raw.get("localization_note") or "").strip()[:800],
    }


def _normalize_ai_analysis(raw: Any) -> list[dict]:
    if not isinstance(raw, list):
        return []
    out: list[dict] = []
    for n in raw:
        if not isinstance(n, dict):
            continue
        verdict = n.get("verdict")
        if verdict not in ("good", "partial", "bad"):
            continue
        doc = (n.get("doc") or "").strip()
        if not doc:
            continue
        score = n.get("compliance_score")
        try:
            score = max(0, min(100, int(score))) if score is not None else None
        except (TypeError, ValueError):
            score = None
        if score is None:
            score = {"good": 85, "partial": 65, "bad": 30}[verdict]

        issues_in = n.get("issues") or []
        issues_out: list[dict] = []
        for is_in in issues_in[:7] if isinstance(issues_in, list) else []:
            if not isinstance(is_in, dict):
                continue
            quote = (is_in.get("quote") or "").strip()
            problem = (is_in.get("problem") or "").strip()
            if not quote or not problem:
                continue
            issues_out.append({
                "quote": quote[:300],
                "article": (is_in.get("article") or "").strip()[:60],
                "problem": problem[:600],
                "fix": (is_in.get("fix") or "").strip()[:600],
            })

        out.append({
            "doc": doc[:80],
            "verdict": verdict,
            "compliance_score": score,
            "summary": (n.get("summary") or "").strip()[:600] or None,
            "text": (n.get("summary") or "").strip()[:600] or None,  # legacy для PDF
            "missing_sections": [str(s).strip()[:200] for s in (n.get("missing_sections") or [])
                                 if isinstance(s, str) and s.strip()][:10],
            "issues": issues_out,
            "strengths": [str(s).strip()[:200] for s in (n.get("strengths") or [])
                          if isinstance(s, str) and s.strip()][:4],
        })
    return out


def assemble(
    crawl: dict[str, Any],
    llm_output: dict[str, Any] | None,
    *,
    report_id: uuid.UUID,
) -> dict[str, Any]:
    """Главная функция: crawl + LLM-output → Контракт №2."""
    pages_crawled = (crawl.get("meta", {}) or {}).get("pages_crawled") or 0
    crawl_status = (crawl.get("meta", {}) or {}).get("status") or ("failed" if pages_crawled == 0 else "ok")

    # Если парсер не смог зайти на сайт — отдельная ветка без LLM.
    if crawl_status == "failed" or pages_crawled == 0:
        return _empty_report(crawl, report_id)

    llm_output = llm_output or {}
    violations = _normalize_violations(llm_output.get("violations"))
    scoring = _normalize_scoring(llm_output.get("scoring"), violations)
    executive = _normalize_executive(llm_output.get("executive_summary"))
    passed_checks = _normalize_passed_checks(llm_output.get("passed_checks"))
    infra = _normalize_infra(llm_output.get("infrastructure_and_geo"), crawl)
    ai_analysis = _normalize_ai_analysis(llm_output.get("ai_analysis"))

    stats = {
        "critical_count": sum(1 for v in violations if v["severity"] == "critical"),
        "warning_count": sum(1 for v in violations if v["severity"] == "warning"),
        "info_count": sum(1 for v in violations if v["severity"] == "info"),
        "passed_count": len(passed_checks),
    }
    total_fine_rub = sum(int(v.get("fine_rub") or 0) for v in violations)

    return {
        "document_meta": _document_meta(crawl, report_id),
        "scoring": scoring,
        "executive_summary": {
            **executive,
            "stats": stats,
            "total_fine_rub": total_fine_rub,
            "passed_checks": passed_checks,
        },
        "infrastructure_and_geo": infra,
        "violations": violations,
        "technical_appendix": {
            "documents_found": _documents_found(crawl),
            "trackers_summary": _trackers_summary(crawl),
            "data_collection_points": _data_collection_points(crawl),
            "ai_analysis": ai_analysis,
        },
        # маркер для фронта/PDF: всё юр-содержание — от AI
        "_ai_powered": True,
    }
