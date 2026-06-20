"""LLM-аналитик: гибрид «код + сфокусированные вызовы LLM».

Архитектура (после рефакторинга на детерминизм):

  1. МЕХАНИЧЕСКИЕ нарушения выписывает КОД (violation_catalog.detect_mechanical)
     по фактам crawl — детерминированно. LLM их не трогает.
  2. СУДИТЕЛЬНЫЕ части отдаём LLM МАЛЕНЬКИМИ сфокусированными вызовами, каждый со
     своим небольшим входом (без 270К текста закона в каждом запросе):
       • по одному вызову на КАЖДЫЙ документ (политика/согласие/cookie) —
         ai_analysis + судительные нарушения по тексту (policy_incomplete,
         no_subject_rights_info, consent_combined_with_ads);
       • один вызов на гео (страна хостинга по IP) → infrastructure_and_geo
         + server_outside_rf;
       • один вызов на итоговое заключение (executive_summary).
     Маленький вход → меньше недетерминизма MoE и выше точность.
  3. Штрафы/severity/статью проставляет CATALOG в report_builder — LLM их не знает.

Каждый под-вызов LLM — best-effort: если он упал (timeout/мусор), пропускаем его,
а отчёт всё равно собирается из механических (кодовых) нарушений. Полностью
отчёт не падает из-за одного под-вызова — это надёжнее прежней схемы «один
большой вызов = всё или ничего».
"""
from __future__ import annotations

import json
import logging
import re
import time as _time
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable

import httpx

from ..config import get_settings
from . import violation_catalog

# Текст 152-ФЗ для ГРАУНДА судительных вызовов. Полный закон НЕ шлём (старый
# дамп ~280K токенов путал модель) — вырезаем только нужную статью под каждый
# тип суждения. Маленький вход + реальный текст закона = юр-точность без
# «потери в середине».
_RESOURCES = Path(__file__).resolve().parent.parent.parent / "resources"
_MAX_ARTICLE_CHARS = 6000

log = logging.getLogger(__name__)


class LLMError(RuntimeError):
    """LLM не вернул валидный ответ на под-вызове (ловится best-effort'ом)."""


# ─────────────────────────────────────────────────────────────────────────────
# Низкоуровневый вызов чата. Маленький системный промпт + маленький user.
# Полный текст закона больше НЕ шлём: штрафы считает код, а судительные правила
# формулируем кратко в каждом промпте (модель знает 152-ФЗ).
# ─────────────────────────────────────────────────────────────────────────────

_DISABLE_THINKING = {
    "thinking": {"type": "disabled"},
    "enable_thinking": False,
    "chat_template_kwargs": {"enable_thinking": False},
}


def _retry_after_sec(resp: httpx.Response, default: float) -> float:
    """Сколько ждать перед ретраем: уважаем заголовок Retry-After (сек), но не
    больше 30с, иначе — экспоненциальный бэкофф по умолчанию."""
    ra = resp.headers.get("Retry-After")
    if ra:
        try:
            return min(float(ra), 30.0)
        except ValueError:
            pass
    return default


def _chat(system: str, user: str, *, max_tokens: int = 3000) -> dict:
    """Один запрос к LLM, JSON-ответ. Поднимает LLMError при сбое."""
    s = get_settings()
    if not s.llm_api_key:
        raise LLMError("LLM_API_KEY is not configured")

    payload = {
        "model": s.llm_model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0,
        "seed": 42,
        "max_tokens": max_tokens,
        **_DISABLE_THINKING,
    }
    headers = {
        "Authorization": f"Bearer {s.llm_api_key}",
        "Content-Type": "application/json",
    }

    last_exc: Exception | None = None
    data: dict | None = None
    for attempt in range(3):
        try:
            with httpx.Client(timeout=httpx.Timeout(s.llm_timeout_sec * 2)) as client:
                r = client.post(f"{s.llm_api_base.rstrip('/')}/chat/completions",
                                json=payload, headers=headers)
                if r.status_code >= 500:
                    raise httpx.HTTPStatusError(
                        f"server {r.status_code}", request=r.request, response=r)
                r.raise_for_status()
                data = r.json()
                break
        except httpx.HTTPStatusError as exc:
            last_exc = exc
            code = exc.response.status_code
            # 429 (rate limit) ретраим тоже — параллельный бёрст под-вызовов
            # делает его вероятнее; уважаем Retry-After.
            if (code == 429 or code >= 500) and attempt < 2:
                wait = _retry_after_sec(exc.response, 2 ** attempt)
                log.warning("LLM %s, retry %d/2 after %.1fs", code, attempt + 1, wait)
                _time.sleep(wait)
                continue
            raise LLMError(f"LLM {code}: {exc.response.text[:200]}") from exc
        except (httpx.ReadTimeout, httpx.WriteError, httpx.RemoteProtocolError,
                httpx.ConnectError) as exc:
            last_exc = exc
            if attempt < 2:
                log.warning("LLM transport error (%s), retry %d/2", type(exc).__name__, attempt + 1)
                _time.sleep(2 ** attempt)
                continue
            raise LLMError(f"LLM transport error after retries: {exc}") from exc
        except httpx.HTTPError as exc:
            raise LLMError(f"LLM transport error: {exc}") from exc
    if data is None:
        raise LLMError(f"LLM exhausted retries: {last_exc}")

    try:
        choice = data["choices"][0]
        content = choice["message"]["content"]
    except (KeyError, IndexError) as exc:
        raise LLMError(f"LLM response without content: {exc}") from exc

    # Обрезка по лимиту токенов → JSON неполный → ниже упадёт парсинг и находки
    # этого документа потеряются. Логируем явно, чтобы это было видно.
    if choice.get("finish_reason") == "length":
        log.warning("LLM output truncated (finish_reason=length) — raise max_tokens")

    try:
        return json.loads(content)
    except json.JSONDecodeError as exc:
        stripped = content.strip().strip("`")
        if stripped.startswith("json"):
            stripped = stripped[4:].lstrip()
        try:
            return json.loads(stripped)
        except json.JSONDecodeError:
            log.warning("LLM returned non-JSON: %r", content[:300])
            raise LLMError(f"LLM returned non-JSON: {exc}") from exc


def _safe(fn: Callable[[], Any], default: Any) -> Any:
    """Best-effort: ошибка под-вызова не валит весь анализ."""
    try:
        return fn()
    except LLMError as exc:
        log.warning("LLM sub-call failed, skipping: %s", exc)
        return default
    except Exception:  # noqa: BLE001
        # неожиданная ошибка (баг в коде под-вызова) — логируем С ТРЕЙСОМ, чтобы
        # best-effort не прятал реальные баги под пустым результатом
        log.exception("LLM sub-call unexpected error, skipping")
        return default


# ─────────────────────────────────────────────────────────────────────────────
# Сбор документов (детерминированный выбор текста)
# ─────────────────────────────────────────────────────────────────────────────

_MAX_DOC_CHARS = 12000


def _collect_documents(crawl: dict[str, Any]) -> dict[str, str]:
    """Тексты политик/согласий/cookie из crawl, детерминированный выбор."""
    out: dict[str, str] = {}
    label_by_kind = {
        "privacy_policy": "Политика конфиденциальности",
        "consent": "Согласие на обработку ПДн",
        "cookie_policy": "Cookie-политика",
    }
    docs = sorted(
        (crawl.get("policy_documents", []) or []),
        key=lambda d: (str(d.get("kind") or ""), str(d.get("url") or "")),
    )
    seen: set[str] = set()
    for doc in docs:
        kind = doc.get("kind")
        if kind not in label_by_kind or kind in seen:
            continue
        text = (doc.get("extracted_text") or "").strip()
        if len(text) < 200:
            continue
        out[label_by_kind[kind]] = text[:_MAX_DOC_CHARS]
        seen.add(kind)

    if "cookie_policy" not in seen:
        pages = sorted((crawl.get("pages", []) or []), key=lambda p: str(p.get("url") or ""))
        for page in pages:
            banner = page.get("cookie_banner") or {}
            txt = (banner.get("full_text") or "").strip()
            if banner.get("present") and len(txt) >= 80:
                out["Cookie-уведомление"] = txt[:_MAX_DOC_CHARS]
                break
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Под-вызов 1: разбор одного документа (ai_analysis + судительные нарушения)
# ─────────────────────────────────────────────────────────────────────────────

@lru_cache(maxsize=1)
def _fz_full() -> str:
    try:
        return (_RESOURCES / "fz_152.txt").read_text(encoding="utf-8")
    except OSError as exc:
        log.warning("fz_152.txt not loaded: %s", exc)
        return ""


@lru_cache(maxsize=32)
def _fz_article(num: str) -> str:
    """Вырезает текст статьи N из 152-ФЗ (от 'Статья N.' до следующей 'Статья \\d').

    Возвращает реальный текст закона под конкретную тему — чтобы судительный
    вызов опирался на статью, а не на «память» модели. Пусто, если не найдено."""
    text = _fz_full()
    if not text:
        return ""
    m = re.search(rf"^Статья {re.escape(num)}\.", text, re.MULTILINE)
    if not m:
        return ""
    nxt = re.search(r"^Статья \d", text[m.end():], re.MULTILINE)
    end = m.end() + nxt.start() if nxt else len(text)
    return text[m.start():end].strip()[:_MAX_ARTICLE_CHARS]


def _articles_block(nums: tuple[str, ...]) -> str:
    parts = [a for a in (_fz_article(n) for n in nums) if a]
    if nums and not parts:
        # ни одна статья не извлеклась (нет файла / переверстали fz_152.txt) —
        # судительный вызов молча упадёт обратно на «память» модели. Сигналим.
        log.warning("law grounding empty for articles %s — fz_152.txt format changed?", nums)
    return ("\n\n".join(parts)) if parts else ""


# Судительные типы по документу + статьи 152-ФЗ для грунта + краткая подсказка.
_DOC_JUDGMENT = {
    "Политика конфиденциальности": {
        "types": ["policy_incomplete", "no_subject_rights_info"],
        "articles": ("18.1", "14"),
        "hint": (
            "policy_incomplete — в политике не хватает обязательных блоков по ст. 18.1 "
            "(цели, правовые основания, категории ПДн/субъектов, сроки хранения и "
            "порядок уничтожения, сведения об операторе).\n"
            "no_subject_rights_info — не раскрыт порядок реализации прав субъекта (ст. 14)."
        ),
    },
    "Согласие на обработку ПДн": {
        "types": ["consent_combined_with_ads"],
        "articles": ("9",),
        "hint": (
            "consent_combined_with_ads — согласие на обработку ПДн совмещено с "
            "согласием на рекламную рассылку в одном чекбоксе (по ст. 9 согласие "
            "должно быть конкретным; разные цели — раздельные согласия)."
        ),
    },
    "Cookie-политика": {"types": [], "articles": (), "hint": ""},
    "Cookie-уведомление": {"types": [], "articles": (), "hint": ""},
}

_DOC_SYSTEM = """\
Ты — практикующий юрист по 152-ФЗ. Тебе дан ТЕКСТ ОДНОГО документа с сайта.
Оцени его и верни ТОЛЬКО JSON (без текста до/после, без markdown, без эмодзи).

{LAW}

Верни:
{
  "analysis": {
    "doc": "<название документа>",
    "verdict": "good" | "partial" | "bad",
    "compliance_score": 0..100,
    "summary": "1-2 предложения",
    "missing_sections": ["обязательные блоки, которых нет"],
    "issues": [
      {"quote": "ТОЧНАЯ цитата из текста ≤220 симв", "article": "ст. X ч. Y",
       "problem": "что не так", "fix": "как исправить"}
    ],
    "strengths": ["0-3 пункта что сделано верно"]
  },
  "violations": [
    {"type": "<один из допустимых>", "description": "...", "evidence": ["..."],
     "recommendation": "..."}
  ]
}

violations — ТОЛЬКО из этого списка типов: {TYPES}. Если документ полон и
претензий нет — violations: []. НЕ выдумывай цитаты: quote и evidence должны
дословно присутствовать в тексте документа.
"""


def _analyze_document(doc_name: str, text: str) -> dict:
    cfg = _DOC_JUDGMENT.get(doc_name, {"types": [], "articles": (), "hint": ""})
    allowed = cfg["types"]
    # Грунт: краткая подсказка + РЕАЛЬНЫЙ текст нужных статей 152-ФЗ.
    law_articles = _articles_block(cfg.get("articles", ()))
    law_block = cfg.get("hint", "")
    if law_articles:
        law_block += "\n\nТЕКСТ СТАТЕЙ 152-ФЗ (опирайся на него, не на память):\n" + law_articles
    system = (
        _DOC_SYSTEM
        .replace("{LAW}", law_block)
        .replace("{TYPES}", ", ".join(allowed) if allowed else "(никаких)")
    )
    user = f"Документ: {doc_name}\n\n--- ТЕКСТ ---\n{text}"
    # 4000: длинная политика с несколькими issues (quote+problem+fix) +
    # missing_sections/strengths легко превышает 2000 → обрезка → потеря разбора.
    res = _chat(system, user, max_tokens=4000)

    analysis = res.get("analysis") if isinstance(res.get("analysis"), dict) else None
    if analysis is not None:
        analysis.setdefault("doc", doc_name)

    violations = []
    for v in (res.get("violations") or []):
        if isinstance(v, dict) and v.get("type") in allowed:
            violations.append(v)
    return {"analysis": analysis, "violations": violations}


# ─────────────────────────────────────────────────────────────────────────────
# Под-вызов 2: гео по IP (infrastructure_and_geo + server_outside_rf)
# ─────────────────────────────────────────────────────────────────────────────

_GEO_SYSTEM = """\
Ты определяешь страну хостинга веб-сайта по IP-адресу сервера. Верни ТОЛЬКО JSON
(без текста до/после, без markdown).

По IP определи страну и провайдера из знаний об ASN/диапазонах. Если НЕ уверен —
ставь null и localization_status="unknown", НЕ гадай.

Верни:
{
  "server_country": "RU" | "US" | ... | null,
  "server_country_ru": "Россия" | "США" | ... | null,
  "hosting_provider": "Selectel LLC" | "Cloudflare, Inc." | ... | null,
  "localization_status": "compliant" | "non_compliant" | "unknown",
  "localization_note": "1-2 предложения с обоснованием, упомяни хостинг по IP"
}

localization_status:
  "non_compliant" — если server_country НЕ "RU" ИЛИ has_cross_border=true.
  "compliant" — server_country=="RU" И has_cross_border=false.
  "unknown" — IP null/страна не определена И has_cross_border=false.
"""


def _analyze_geo(crawl: dict[str, Any]) -> dict:
    meta = crawl.get("meta", {}) or {}
    summary = crawl.get("summary", {}) or {}
    server_ip = meta.get("server_ip")
    has_cross = bool(summary.get("has_cross_border_transfer")) or any(
        t.get("cross_border") for t in (summary.get("trackers") or [])
    )
    if not server_ip:
        # Без IP гео определить нельзя — не дёргаем LLM.
        return {
            "infrastructure_and_geo": {
                "server_country": None, "server_country_ru": None,
                "hosting_provider": None,
                "localization_status": "non_compliant" if has_cross else "unknown",
                "localization_note": "",
            },
            "violations": [],
        }

    user = f"server_ip: {server_ip}\nhas_cross_border: {str(has_cross).lower()}"
    geo = _chat(_GEO_SYSTEM, user, max_tokens=400)
    geo = geo if isinstance(geo, dict) else {}

    violations: list[dict] = []
    # server_outside_rf выписываем только если сайт обрабатывает ПДн и страна не РФ.
    country = (geo.get("server_country") or "").upper()
    if (country and country != "RU" and violation_catalog.processes_pii(crawl)):
        violations.append({
            "type": "server_outside_rf",
            "description": (
                f"Сервер сайта расположен за пределами РФ "
                f"({geo.get('server_country_ru') or country}), что нарушает "
                f"требование локализации баз ПДн (ст. 18 ч. 5 152-ФЗ)."
            ),
            "evidence": [
                f"server_ip: {server_ip}",
                f"server_country: {country}",
                *( [f"hosting_provider: {geo.get('hosting_provider')}"] if geo.get("hosting_provider") else [] ),
            ],
            "recommendation": (
                "Перенесите базы данных с ПДн на серверы, расположенные на "
                "территории РФ (ст. 18 ч. 5 152-ФЗ)."
            ),
        })

    return {
        "infrastructure_and_geo": {
            "server_country": geo.get("server_country"),
            "server_country_ru": geo.get("server_country_ru"),
            "hosting_provider": geo.get("hosting_provider"),
            "localization_status": geo.get("localization_status") or "unknown",
            "localization_note": geo.get("localization_note") or "",
        },
        "violations": violations,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Под-вызов 3: итоговое заключение
# ─────────────────────────────────────────────────────────────────────────────

_EXEC_SYSTEM = """\
Ты — юрист по 152-ФЗ. По списку выявленных нарушений и кратким фактам сайта
напиши итоговое заключение аудита. Верни ТОЛЬКО JSON (без markdown, без эмодзи):
{"verdict": "2-4 предложения юридическим языком",
 "verdict_plain": "2-3 предложения простыми словами без жаргона"}

Если нарушений нет и сайт не обрабатывает ПДн — напиши, что требования 152-ФЗ к
нему не применяются. Не придумывай нарушений сверх переданного списка.
"""


def _exec_summary(crawl: dict[str, Any], violations: list[dict]) -> dict | None:
    s = crawl.get("summary", {}) or {}
    titles = [f"- {v.get('title') or v.get('type')}" for v in violations]
    facts = (
        f"Форм с ПДн: {s.get('forms_collecting_pii') or 0}; "
        f"трекеров: {len(s.get('trackers') or [])}; "
        f"политика опубликована: {'да' if s.get('has_privacy_policy') else 'нет'}; "
        f"обрабатывает ПДн: {'да' if violation_catalog.processes_pii(crawl) else 'нет'}."
    )
    viol_block = "\n".join(titles) if titles else "(нарушений не выявлено)"
    user = f"ФАКТЫ: {facts}\n\nВЫЯВЛЕННЫЕ НАРУШЕНИЯ:\n{viol_block}"
    res = _chat(_EXEC_SYSTEM, user, max_tokens=600)
    res = res if isinstance(res, dict) else {}
    if res.get("verdict"):
        return {"verdict": res.get("verdict"), "verdict_plain": res.get("verdict_plain") or res.get("verdict")}
    return None  # LLM не дала вердикт → пусть оркестратор подставит fallback (и учтёт деградацию)


def _fallback_verdict(crawl: dict[str, Any], violations: list[dict]) -> dict:
    """Детерминированный вердикт, если LLM-вызов заключения не удался."""
    if not violations:
        if not violation_catalog.processes_pii(crawl):
            v = ("Сайт не обрабатывает персональные данные: отсутствуют формы "
                 "сбора ПДн и сторонние трекеры. Требования 152-ФЗ к нему не применяются.")
        else:
            v = "Существенных нарушений требований 152-ФЗ не выявлено."
        return {"verdict": v, "verdict_plain": v}
    n = len(violations)
    v = (f"Выявлено нарушений требований 152-ФЗ: {n}. Рекомендуется устранить их "
         f"для снижения рисков административной ответственности по КоАП ст. 13.11.")
    return {"verdict": v, "verdict_plain": v}


# ─────────────────────────────────────────────────────────────────────────────
# Оркестратор — точка входа (совместима с прежним call_llm)
# ─────────────────────────────────────────────────────────────────────────────


def call_llm(crawl: dict[str, Any]) -> dict[str, Any]:
    """Возвращает llm_output в прежнем формате (violations, ai_analysis,
    infrastructure_and_geo, executive_summary, passed_checks) — но механика
    выписывается кодом, а судительные части — маленькими вызовами LLM."""
    s = get_settings()
    if not s.llm_api_key:
        raise LLMError("LLM_API_KEY is not configured")

    # 1) Механические нарушения — код (детерминированно).
    violations: list[dict] = list(violation_catalog.detect_mechanical(crawl))

    # 2-3) Разбор документов + гео — НЕЗАВИСИМЫЕ под-вызовы, гоним ПАРАЛЛЕЛЬНО,
    # но max_workers=2: ограничиваем бёрст, чтобы не провоцировать 429 у провайдера
    # (429 теперь ретраится в _chat, но меньше параллелизма — меньше шанс).
    docs = _collect_documents(crawl)
    has_server_ip = bool((crawl.get("meta", {}) or {}).get("server_ip"))
    llm_attempts = len(docs) + (1 if has_server_ip else 0)
    llm_ok = 0
    ai_analysis: list[dict] = []
    with ThreadPoolExecutor(max_workers=2) as ex:
        doc_futures = {
            name: ex.submit(_safe, lambda n=name, t=text: _analyze_document(n, t), {})
            for name, text in docs.items()
        }
        geo_future = ex.submit(_safe, lambda: _analyze_geo(crawl), {})

        for name, fut in doc_futures.items():
            res = fut.result()
            if res:  # непустой → под-вызов отработал (на сбое _safe вернёт {})
                llm_ok += 1
            if res.get("analysis"):
                ai_analysis.append(res["analysis"])
            violations.extend(res.get("violations", []))

        geo = geo_future.result()
    if has_server_ip and geo:
        llm_ok += 1
    infra = geo.get("infrastructure_and_geo") or {}
    violations.extend(geo.get("violations", []))

    # Взаимоисключение локализационных нарушений: cross_border_transfer (факт
    # парсера: зарубежные трекеры) и server_outside_rf (догадка LLM о стране) —
    # это одна и та же ст. 18 ч. 5 и один и тот же штраф. Если есть оба — оставляем
    # cross_border_transfer (на факте), убираем server_outside_rf, чтобы не
    # удваивать штраф/score за одну проблему локализации.
    vtypes = {v.get("type") for v in violations}
    if "cross_border_transfer" in vtypes and "server_outside_rf" in vtypes:
        violations = [v for v in violations if v.get("type") != "server_outside_rf"]

    # 4) Пройденные проверки — код (детерминированно).
    passed = violation_catalog.passed_checks(crawl, violations)

    # 5) Итоговое заключение — зависит от итогового списка нарушений, поэтому
    # ПОСЛЕ параллельной фазы. Это тоже LLM-под-вызов — учитываем в деградации:
    # на сбое/без вердикта подставляем детерминированный fallback.
    llm_attempts += 1
    exec_res = _safe(lambda: _exec_summary(crawl, violations), None)
    if exec_res:
        llm_ok += 1
        executive = exec_res
    else:
        executive = _fallback_verdict(crawl, violations)

    # Деградация: были LLM-под-вызовы, но НИ ОДИН не удался (полный отказ
    # провайдера) → отчёт собран из механики + fallback, реального AI-разбора нет.
    # Не выдаём его за AI-powered (см. report_builder).
    ai_degraded = llm_attempts > 0 and llm_ok == 0
    if ai_degraded:
        log.warning("all %d LLM sub-calls failed — report is mechanical-only", llm_attempts)

    return {
        "violations": violations,
        "ai_analysis": ai_analysis,
        "infrastructure_and_geo": infra,
        "executive_summary": executive,
        "passed_checks": passed,
        "_ai_degraded": ai_degraded,
    }
