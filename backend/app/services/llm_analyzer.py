"""LLM-аналитик: единственный источник юр-вердиктов в продукте.

Алгоритм НЕ выносит решений «нарушение / не нарушение» — он только подаёт LLM:
  - факты со сайта (CrawlJSON из парсера);
  - тексты найденных политик/согласий/cookie;
  - полный 152-ФЗ;
  - полный КоАП ст. 13.11 (для сумм штрафов).

LLM возвращает структурированный JSON (см. _RESPONSE_SCHEMA): нарушения, скоринг,
вердикт, AI-разбор документов. Дальше report_builder.py сшивает это с
алгоритмическими частями (метаданные парсера, перечень трекеров и форм) в
финальный Контракт №2.

Если что-то идёт не так (timeout, мусорный JSON) — поднимаем LLMError, и
вызывающий таск пометит скан failed. Никакого fallback на «детерминированные
правила» нет — это была установка заказчика.
"""
from __future__ import annotations

import json
import logging
from functools import lru_cache
from pathlib import Path
from typing import Any

import httpx

from ..config import get_settings

log = logging.getLogger(__name__)


class LLMError(RuntimeError):
    """LLM не вернул валидный ответ. Скан в этом случае помечается failed."""


# ─────────────────────────────────────────────────────────────────────────────
# Тексты законов (грузим один раз при импорте — это десятки килобайт, но они
# нужны на каждый вызов; держать в памяти дешевле, чем читать с диска каждый раз)
# ─────────────────────────────────────────────────────────────────────────────

# app/services/llm_analyzer.py → … → backend/resources/
# Path(__file__) = backend/app/services/llm_analyzer.py
# .parent = services, .parent.parent = app, .parent.parent.parent = backend (= WORKDIR /app в контейнере)
_RESOURCES = Path(__file__).resolve().parent.parent.parent / "resources"


@lru_cache(maxsize=1)
def _law_texts() -> tuple[str, str]:
    fz = (_RESOURCES / "fz_152.txt").read_text(encoding="utf-8")
    koap = (_RESOURCES / "koap_13_11.txt").read_text(encoding="utf-8")
    return fz, koap


# ─────────────────────────────────────────────────────────────────────────────
# Системный промпт. Стабильная часть — закон + правила. Меняется редко, поэтому
# хорошо кешируется prompt-cache'ом провайдера (DeepSeek авто-кеш TTL 5 мин).
# ─────────────────────────────────────────────────────────────────────────────

_SYSTEM_HEADER = """\
Ты — практикующий юрист по российскому законодательству о персональных данных
(152-ФЗ и КоАП РФ). Твоя задача — оценить веб-сайт компании на риски нарушения
152-ФЗ на основании фактов, собранных автоматическим парсером, и текстов
документов с этого сайта.

═════════════════════════════════════════════════════════════════════════════
ГЛАВНОЕ ПРАВИЛО — НЕ ШТРАФУЙ САЙТЫ, КОТОРЫЕ НЕ ОБРАБАТЫВАЮТ ПДН
═════════════════════════════════════════════════════════════════════════════

152-ФЗ применяется только к ОПЕРАТОРАМ персональных данных. Сайт не является
оператором, если на нём:
  - НЕТ форм, собирающих персональные данные (имя, телефон, email, паспорт, …);
  - НЕТ сторонних трекеров/аналитики/чат-виджетов (Яндекс.Метрика, Google
    Analytics, Tag Manager, чат-боты и т.п.);
  - НЕТ сторонних cookie третьих лиц;
  - НЕТ авторизации / личных кабинетов.

Если по фактам парсера всё это отсутствует — НЕ выписывай нарушения вида
«нет политики», «нет cookie-баннера», «не идентифицирован оператор». Сайт без
обработки ПДн НЕ ОБЯЗАН иметь политику. В этом случае верни:
  - violations: []
  - scoring.overall_score: 100, risk_level: "SAFE", risk_label_ru: "Соответствует"
  - executive_summary.verdict: «Сайт не обрабатывает персональные данные:
    отсутствуют формы сбора ПДн, сторонние трекеры и cookie третьих лиц.
    Требования 152-ФЗ к нему не применяются.»
  - executive_summary.verdict_plain — то же простыми словами.

ИСКЛЮЧЕНИЕ: даже у сайта-визитки есть Яндекс.Метрика — он уже обрабатывает
технические ПДн (cookie + IP) и должен иметь политику. Анализируй каждый
случай отдельно.

═════════════════════════════════════════════════════════════════════════════
ПРАВИЛА ОФОРМЛЕНИЯ ОТВЕТА
═════════════════════════════════════════════════════════════════════════════

Язык: русский, юридический, но понятный SMB-владельцу сайта. Пиши «оператор
обязан», «рекомендуется», не «вы должны».

ЗАПРЕЩЕНО: markdown, **жирный**, эмодзи, обратные апострофы, заголовки,
маркированные списки внутри строковых полей.

КАК РАБОТАЮТ НАРУШЕНИЯ (ВАЖНО — ИЗМЕНЕНО):

Ты НЕ присваиваешь severity, статью и штраф. Ты только ОПРЕДЕЛЯЕШЬ ТИП
нарушения из фиксированного списка ниже и описываешь его конкретику.
Серьёзность, статью 152-ФЗ и сумму штрафа проставит система автоматически по
типу. Это нужно для объективности и юридической защиты оценки.

Каждый объект violations[] содержит:

  type — строго ОДИН код из списка допустимых типов (см. ниже). Если факт не
    подпадает ни под один тип — НЕ выписывай нарушение.
  title — краткий заголовок ≤ 80 символов под конкретный сайт (необязательно;
    если не уверен — пропусти, система подставит дефолтный).
  description — 1-3 предложения: что именно не так на ЭТОМ сайте.
  evidence — массив 1-5 строк. КАЖДАЯ строка — конкретный факт ИЗ CRAWLJSON
    или цитата из приложенных документов. ЗАПРЕЩЕНО:
      • придумывать имена cookie/трекеров, которых нет в crawl;
      • ссылаться на кнопки/формы/URL, которых нет в crawl;
      • использовать свои знания о популярных сайтах.
    Нет конкретного факта в crawl — пиши обобщённо.
  recommendation — 1-3 предложения, ЧТО КОНКРЕТНО сделать.

ОДИН ТИП — ОДНО НАРУШЕНИЕ. Не выписывай один и тот же type дважды, даже если
проблема встречается на многих страницах (опиши масштаб в description/evidence).

ДОПУСТИМЫЕ ТИПЫ НАРУШЕНИЙ (поле type):

  cross_border_transfer    — на сайте зарубежные трекеры/сервисы (Google
                             Analytics/Tag Manager/reCAPTCHA, Facebook, TikTok и
                             т.п.) ИЛИ summary.has_cross_border_transfer=true.
  server_outside_rf        — meta.server_ip принадлежит хостингу ВНЕ РФ (по IP
                             определи страну; если НЕ РФ — этот тип). Если сервер
                             в РФ, но есть зарубежные трекеры — используй
                             cross_border_transfer, а этот НЕ выписывай.
  prechecked_consent       — чекбокс согласия проставлен по умолчанию
                             (pre_checked=true / forms_with_prechecked_consent>0).
  form_without_consent     — форма собирает ПДн без чекбокса согласия
                             (forms_pii_without_consent>0).
  tracking_before_consent  — трекеры срабатывают до согласия
                             (tracking_before_consent=true).
  consent_combined_with_ads— согласие на ПДн совмещено с согласием на рекламу.
  no_privacy_policy         — политика обработки ПДн НЕ найдена, ХОТЯ сайт
                             обрабатывает ПДн (has_privacy_policy=false).
  policy_incomplete         — политика есть, но неполная: нет сроков хранения,
                             порядка уничтожения, прав субъекта и т.п. (по тексту).
  no_operator_identification— оператор ПДн не идентифицирован (нет названия
                             юрлица / ИНН / ОГРН в site_identity).
  cookie_no_reject          — cookie-баннер есть, но без кнопки «Отклонить»
                             (cookie_banner_has_reject=false).
  no_cookie_notice          — cookie-баннер вообще отсутствует
                             (has_cookie_banner=false), но сайт ставит cookie.
  captcha_no_notice         — используется captcha (трекер category=captcha) без
                             уведомления об обработке данных.
  no_rkn_notification       — нет признаков уведомления Роскомнадзора об обработке
                             ПДн (выписывай только если сайт явно обрабатывает ПДн).
  no_subject_rights_info    — не раскрыт порядок реализации прав субъекта ПДн
                             (доступ, изменение, удаление, отзыв согласия).

executive_summary.verdict — 2-4 предложения юридическим языком.
executive_summary.verdict_plain — 2-3 предложения простыми словами без жаргона.

Скоринг (overall_score, risk_level, legal_score, technical_score) НЕ считай —
система посчитает сама по типам нарушений. В ответе эти поля можешь не указывать
или оставить 0.

═════════════════════════════════════════════════════════════════════════════
INFRASTRUCTURE_AND_GEO — ОПРЕДЕЛИ СТРАНУ И ХОСТИНГ ПО IP САМ
═════════════════════════════════════════════════════════════════════════════

В CrawlJSON может быть meta.server_ip — реальный IP, к которому подключился
браузер при загрузке сайта. По этому IP ТЫ определяешь страну хостинга и
провайдера (Cloudflare, AWS, Yandex.Cloud, Selectel и т.п.) из своих знаний
о известных IP-диапазонах ASN.

Заполни в ответе поля:
  server_country     — ISO-2 ("RU", "US", "DE", "NL", ...) или null, если не уверен
  server_country_ru  — русское название ("Россия", "США", "Германия") или null
  hosting_provider   — имя провайдера ("Cloudflare, Inc.", "Selectel LLC") или null

Если ты НЕ ЗНАЕШЬ точно, чей это IP — ставь null, не гадай.

localization_status (для соответствия ст. 18 ч. 5 152-ФЗ):

  "non_compliant" — если ВЫПОЛНЕНО хотя бы одно из условий:
    • ты определил, что server_country НЕ равен "RU";
    • есть зарубежные трекеры (cross_border=true в trackers[]) ИЛИ
      has_cross_border_transfer=true в summary.
    Это нарушение ст. 18 ч. 5 152-ФЗ. Штраф по КоАП ст. 13.11 ч. 8 — до
    6 000 000 ₽ для юрлица. Выпиши отдельный violation с этой суммой,
    target_role="developer".

  "compliant"     — server_country == "RU" И нет зарубежных трекеров.
                    Только в этом случае ставь compliant.

  "unknown"       — server_ip null ИЛИ ты не смог определить страну
                    (поставил server_country=null) И нет зарубежных трекеров.
                    Не ставь "compliant" без подтверждения.

localization_note — 1-2 предложения с обоснованием. Если знаешь хостинг —
упомяни его явно: «IP 172.67.198.243 принадлежит Cloudflare, Inc. (США) —
ПДн обрабатываются вне территории РФ».

═════════════════════════════════════════════════════════════════════════════
AI_ANALYSIS — РАЗБОР ДОКУМЕНТОВ С САЙТА
═════════════════════════════════════════════════════════════════════════════

Для каждого присланного текста (политика, согласие, cookie) сделай отдельный
объект в массиве ai_analysis. Поля:
  doc — название документа ("Политика конфиденциальности", "Согласие на
    обработку ПДн", "Cookie-уведомление")
  verdict: "good" | "partial" | "bad"
  compliance_score: 0-100 (good ≥ 80, partial 50-79, bad < 50)
  summary: 1-2 предложения общим планом
  missing_sections: массив строк — обязательные блоки 152-ФЗ, которых нет
  issues: массив объектов {quote, article, problem, fix}, где
    quote — ТОЧНАЯ цитата из документа (≤ 220 символов), не выдумывай
    article — статья закона "ст. X ч. Y"
    problem — что не так с цитатой (1-2 предложения)
    fix — как исправить (1-2 предложения)
  strengths: массив 0-3 пунктов что в документе сделано правильно

Если документа НЕТ — НЕ создавай для него объект в ai_analysis.

═════════════════════════════════════════════════════════════════════════════
СХЕМА ОТВЕТА (СТРОГО JSON, БЕЗ ТЕКСТА ДО ИЛИ ПОСЛЕ)
═════════════════════════════════════════════════════════════════════════════

{
  "infrastructure_and_geo": {
    "server_country": "RU" | "US" | ... | null,
    "server_country_ru": "Россия" | "США" | ... | null,
    "hosting_provider": "Cloudflare, Inc." | ... | null,
    "localization_status": "compliant" | "non_compliant" | "unknown",
    "localization_note": "..."
  },
  "violations": [
    {
      "type": "cross_border_transfer",
      "title": "...",
      "description": "...",
      "evidence": ["...", "..."],
      "recommendation": "..."
    }
  ],
  "passed_checks": [
    {"title": "...", "detail": "..."}
  ],
  "executive_summary": {
    "verdict": "...",
    "verdict_plain": "..."
  },
  "ai_analysis": [
    {
      "doc": "...",
      "verdict": "good" | "partial" | "bad",
      "compliance_score": 0..100,
      "summary": "...",
      "missing_sections": ["..."],
      "issues": [
        {"quote": "...", "article": "ст. X ч. Y", "problem": "...", "fix": "..."}
      ],
      "strengths": ["..."]
    }
  ]
}

═════════════════════════════════════════════════════════════════════════════
ТЕКСТ ЗАКОНА 152-ФЗ (ред. от 24.06.2025)
═════════════════════════════════════════════════════════════════════════════

{FZ_152}

═════════════════════════════════════════════════════════════════════════════
ТЕКСТ КоАП РФ СТ. 13.11 (актуальная редакция с поправками ФЗ 420-ФЗ от
30.11.2024, действует с 30.05.2025)
═════════════════════════════════════════════════════════════════════════════

{KOAP}
"""


@lru_cache(maxsize=1)
def _system_prompt() -> str:
    fz, koap = _law_texts()
    return _SYSTEM_HEADER.replace("{FZ_152}", fz).replace("{KOAP}", koap)


# ─────────────────────────────────────────────────────────────────────────────
# Подготовка фактов для LLM
# ─────────────────────────────────────────────────────────────────────────────

# Максимальный размер одного текста документа, чтобы не раздувать input.
_MAX_DOC_CHARS = 12000


def _collect_documents(crawl: dict[str, Any]) -> dict[str, str]:
    """Достаём из crawl тексты политик/согласий/cookie, обрезая по длине.

    Выбор детерминирован: документы сортируются по url, так что для одного
    сайта при повторном скане в LLM уходит ровно тот же текст (важно для
    воспроизводимой оценки)."""
    out: dict[str, str] = {}
    label_by_kind = {
        "privacy_policy": "Политика конфиденциальности",
        "consent": "Согласие на обработку ПДн",
        "cookie_policy": "Cookie-политика",
    }
    # Стабильный порядок: сортируем по (kind, url).
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

    # Cookie-баннер — только если не было отдельной cookie-policy. Берём первый
    # по отсортированному url, чтобы выбор не зависел от порядка обхода.
    if "cookie_policy" not in seen:
        pages = sorted(
            (crawl.get("pages", []) or []),
            key=lambda p: str(p.get("url") or ""),
        )
        for page in pages:
            banner = page.get("cookie_banner") or {}
            txt = (banner.get("full_text") or "").strip()
            if banner.get("present") and len(txt) >= 80:
                out["Cookie-уведомление"] = txt[:_MAX_DOC_CHARS]
                break

    return out


# Нестабильные поля meta — меняются от скана к скану, на анализ не влияют.
# Вырезаем перед отправкой LLM, чтобы одинаковый сайт давал одинаковый вход.
_VOLATILE_META = ("scan_id", "started_at", "finished_at", "duration_ms", "errors")


def _slim_crawl(crawl: dict[str, Any]) -> dict[str, Any]:
    """Готовим CrawlJSON для LLM в ДЕТЕРМИНИРОВАННОМ виде.

    Зачем: два скана одного сайта возвращают одни и те же факты, но в разном
    порядке (BFS-обход непредсказуем) и с разными timestamps. Без нормализации
    LLM видит разный JSON → даёт разную оценку даже при seed=42 и temperature=0.

    Что делаем:
      1) рекурсивно сортируем ключи (sort_keys при дампе);
      2) сортируем массивы объектов (pages, forms, trackers...) по их же
         каноническому виду — стабильный порядок;
      3) выкидываем volatile-поля meta (scan_id, время) — не влияют на вердикт;
      4) убираем extracted_text политик (уходит отдельным блоком).
    """
    # Глубокая копия через json round-trip (заодно отсекает несериализуемое).
    slim = json.loads(json.dumps(crawl, ensure_ascii=False, default=str))

    meta = slim.get("meta")
    if isinstance(meta, dict):
        for k in _VOLATILE_META:
            meta.pop(k, None)

    # policy_documents — без extracted_text (большой текст идёт отдельно).
    if isinstance(slim.get("policy_documents"), list):
        for d in slim["policy_documents"]:
            if isinstance(d, dict):
                d.pop("extracted_text", None)

    _sort_arrays_in_place(slim)
    return slim


def _sort_arrays_in_place(node: Any) -> None:
    """Рекурсивно сортирует все списки объектов/словарей по их каноническому
    json-представлению. Списки примитивов (строк/чисел) тоже сортируем."""
    if isinstance(node, dict):
        for v in node.values():
            _sort_arrays_in_place(v)
    elif isinstance(node, list):
        for v in node:
            _sort_arrays_in_place(v)
        try:
            node.sort(key=lambda x: json.dumps(x, ensure_ascii=False, sort_keys=True, default=str))
        except TypeError:
            pass


def _build_user_message(crawl: dict[str, Any]) -> str:
    docs = _collect_documents(crawl)
    slim = _slim_crawl(crawl)

    parts: list[str] = [
        "Проанализируй сайт по фактам ниже. Верни ТОЛЬКО JSON по схеме из системного промпта.",
        "",
        "═══ ФАКТЫ С САЙТА (CrawlJSON) ═══",
        # sort_keys=True — ключи в стабильном порядке (детерминизм входа).
        json.dumps(slim, ensure_ascii=False, indent=2, sort_keys=True),
    ]
    if docs:
        parts.append("")
        parts.append("═══ ТЕКСТЫ НАЙДЕННЫХ ДОКУМЕНТОВ ═══")
        for name, text in docs.items():
            parts.append("")
            parts.append(f"--- {name} ---")
            parts.append(text)
    else:
        parts.append("")
        parts.append("═══ ТЕКСТЫ ДОКУМЕНТОВ ═══")
        parts.append("На сайте не найдено политики/согласия/cookie-уведомления.")

    return "\n".join(parts)


# ─────────────────────────────────────────────────────────────────────────────
# Вызов LLM
# ─────────────────────────────────────────────────────────────────────────────

# Явно выключаем thinking/reasoning-режим. У провайдеров формат разный, шлём
# все три варианта — каждый поймёт свой, чужой проигнорирует:
#   • DeepSeek V4: "thinking": {"type": "disabled"}
#   • DashScope (Alibaba Qwen, OpenAI-compat): "enable_thinking": false (в корне)
#   • Self-hosted vLLM/SGLang Qwen: "chat_template_kwargs.enable_thinking": false
# Без этого qwen3.6-plus на DashScope включает thinking по умолчанию →
# генерирует сотни reasoning-токенов на простой запрос → broken pipe / timeout.
_DISABLE_THINKING = {
    "thinking": {"type": "disabled"},
    "enable_thinking": False,
    "chat_template_kwargs": {"enable_thinking": False},
}


def call_llm(crawl: dict[str, Any]) -> dict[str, Any]:
    """Синхронный вызов LLM. Возвращает разобранный JSON или поднимает LLMError."""
    s = get_settings()
    if not s.llm_api_key:
        raise LLMError("LLM_API_KEY is not configured")

    payload = {
        "model": s.llm_model,
        "messages": [
            {"role": "system", "content": _system_prompt()},
            {"role": "user", "content": _build_user_message(crawl)},
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0,
        # На сайт с 5-7 нарушениями + AI-анализом 3 документов уходит ~5-8К
        # выходных токенов. Берём 8000 — хватит даже при подробных fix'ах.
        "seed": 42,
        "max_tokens": 8000,
        **_DISABLE_THINKING,
    }
    headers = {
        "Authorization": f"Bearer {s.llm_api_key}",
        "Content-Type": "application/json",
    }

    # Ретраи на transient-ошибки. broken pipe / connection reset / read timeout
    # бывают у DashScope при больших контекстах. 5xx тоже ретраим — обычно
    # перегрузка балансировщика. На 4xx (включая 401) не ретраим — это конфиг.
    import time as _time
    last_exc: Exception | None = None
    for attempt in range(3):
        try:
            with httpx.Client(timeout=httpx.Timeout(s.llm_timeout_sec * 3)) as client:
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
            if exc.response.status_code >= 500 and attempt < 2:
                log.warning("LLM %s, retry %d/2", exc.response.status_code, attempt + 1)
                _time.sleep(2 ** attempt)
                continue
            raise LLMError(f"LLM {exc.response.status_code}: {exc.response.text[:200]}") from exc
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
    else:
        raise LLMError(f"LLM exhausted retries: {last_exc}")

    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as exc:
        raise LLMError(f"LLM response without content: {exc}") from exc

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as exc:
        # На всякий случай вырежем возможные markdown-обёртки ```json ... ```
        stripped = content.strip().strip("`")
        if stripped.startswith("json"):
            stripped = stripped[4:].lstrip()
        try:
            parsed = json.loads(stripped)
        except json.JSONDecodeError:
            log.warning("LLM returned non-JSON content: %r", content[:500])
            raise LLMError(f"LLM returned non-JSON: {exc}") from exc

    return parsed
