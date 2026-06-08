"""LLM-анализ текстов политик и согласий (paid-tier).

Любой OpenAI-совместимый API: DeepSeek, Qwen/DashScope, OpenAI, локальный vLLM.
Конфиг — три env-переменные: LLM_API_BASE, LLM_API_KEY, LLM_MODEL.

Что анализируется (берём из Контракта №1 = crawler JSON):
    - policy_documents[kind=privacy_policy].extracted_text — политика;
    - policy_documents[kind=consent].extracted_text     — согласие (если есть);
    - policy_documents[kind=cookie_policy].extracted_text ИЛИ cookie_banner.full_text — cookie.

На выходе — список AiNote по Контракту №2 (см. PDFreport/models.py::AiNote):
    {"doc": "...", "verdict": "good"|"partial"|"bad", "text": "..."}

Ошибки/таймауты глушим — отчёт всё равно отдаём, просто без AI-разбора.
"""
from __future__ import annotations

import json
import logging
from typing import Any

import httpx

from ..config import get_settings

log = logging.getLogger(__name__)

# Чтобы не словить лимит токенов и не дорого платить.
_MAX_DOC_CHARS = 6000
_MAX_DOCS = 3

_SYSTEM = (
    "Ты — юрист по 152-ФЗ «О персональных данных» РФ. На вход — текст документа с сайта "
    "(политика конфиденциальности, согласие на обработку ПДн или cookie-уведомление). "
    "Оцени, насколько документ соответствует требованиям 152-ФЗ. "
    "Ответ строго в JSON: {\"verdict\": \"good\"|\"partial\"|\"bad\", \"text\": \"...\"}. "
    "verdict=good — если документ полностью покрывает цели обработки, сроки хранения, "
    "права субъекта ПДн и передачу третьим лицам. partial — если что-то существенное "
    "не раскрыто. bad — если документ формальный/обобщённый или ключевые блоки отсутствуют. "
    "В поле text — 2-3 предложения по-русски: что именно хорошо/плохо. Без воды."
)


def _collect_docs(crawl: dict[str, Any]) -> list[dict[str, str]]:
    """Достаём из Контракта №1 тексты, которые имеет смысл прогонять через LLM."""
    out: list[dict[str, str]] = []

    label = {
        "privacy_policy": "Политика конфиденциальности",
        "consent": "Согласие на обработку ПДн",
        "cookie_policy": "Cookie-политика",
    }

    seen_kinds: set[str] = set()
    for doc in crawl.get("policy_documents", []) or []:
        kind = doc.get("kind")
        if kind not in label or kind in seen_kinds:
            continue
        text = (doc.get("extracted_text") or "").strip()
        if len(text) < 200:  # слишком короткие пропускаем — нечего разбирать
            continue
        out.append({"doc": label[kind], "text": text[:_MAX_DOC_CHARS]})
        seen_kinds.add(kind)
        if len(out) >= _MAX_DOCS:
            return out

    # Cookie-баннер как fallback, если не было cookie_policy
    if "cookie_policy" not in seen_kinds and len(out) < _MAX_DOCS:
        for page in crawl.get("pages", []) or []:
            banner = page.get("cookie_banner") or {}
            ftxt = (banner.get("full_text") or "").strip()
            if banner.get("present") and len(ftxt) >= 80:
                out.append({"doc": "Cookie-уведомление", "text": ftxt[:_MAX_DOC_CHARS]})
                break

    return out


def _call_llm(text: str) -> dict[str, str] | None:
    """Один синхронный POST в /chat/completions. Возвращает разобранный JSON или None."""
    s = get_settings()
    if not s.llm_api_key:
        return None

    payload = {
        "model": s.llm_model,
        "messages": [
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": text},
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.2,
        "max_tokens": 400,
    }
    headers = {
        "Authorization": f"Bearer {s.llm_api_key}",
        "Content-Type": "application/json",
    }

    try:
        with httpx.Client(timeout=httpx.Timeout(s.llm_timeout_sec)) as client:
            r = client.post(f"{s.llm_api_base.rstrip('/')}/chat/completions",
                            json=payload, headers=headers)
            r.raise_for_status()
            data = r.json()
    except httpx.HTTPError as exc:
        log.warning("LLM call failed: %s", exc)
        return None

    try:
        content = data["choices"][0]["message"]["content"]
        parsed = json.loads(content)
    except (KeyError, IndexError, json.JSONDecodeError) as exc:
        log.warning("LLM bad response: %s", exc)
        return None

    verdict = parsed.get("verdict")
    txt = parsed.get("text")
    if verdict not in ("good", "partial", "bad") or not isinstance(txt, str):
        log.warning("LLM verdict invalid: %r", parsed)
        return None
    return {"verdict": verdict, "text": txt.strip()}


def analyze(crawl: dict[str, Any]) -> list[dict[str, Any]]:
    """Главная точка входа: вернёт ai_analysis для technical_appendix.

    Никогда не падает — в худшем случае вернёт пустой список и залогирует warning.
    """
    s = get_settings()
    if not s.llm_api_key:
        return []

    docs = _collect_docs(crawl)
    if not docs:
        return []

    notes: list[dict[str, Any]] = []
    for d in docs:
        res = _call_llm(d["text"])
        if res is None:
            continue
        notes.append({"doc": d["doc"], "verdict": res["verdict"], "text": res["text"]})

    return notes
