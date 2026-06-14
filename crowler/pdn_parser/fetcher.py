"""Загрузка страницы через Playwright с перехватом cookie и сетевых запросов.

Каждая страница грузится в свежем browser-контексте: так cookie, выставленные
сайтом, и запросы к третьим лицам отражают ровно один первичный визит
(важно для аудита «что ставится до согласия»).
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from playwright.async_api import Browser, Error as PlaywrightError

from .signatures import MODAL_TRIGGER_KEYWORDS

DEFAULT_UA = (
    "Mozilla/5.0 (compatible; PDnControlBot/0.1; +https://example.com/bot) "
    "Chrome/120.0 Safari/537.36"
)


@dataclass
class FetchResult:
    url: str
    final_url: str
    status: int | None
    html: str = ""
    title: str = ""
    cookies: list[dict] = field(default_factory=list)
    request_urls: list[str] = field(default_factory=list)
    links: list[str] = field(default_factory=list)
    # HTML-снимки DOM после клика по каждой кнопке-триггеру модалки. Каждый
    # снимок отдельно прогоняется через detect_forms — так в аудит попадают
    # формы, которых нет в статическом DOM до взаимодействия.
    modal_html: list[str] = field(default_factory=list)
    error: str | None = None
    # IP сервера, к которому реально подключился Playwright при загрузке этой
    # страницы. Берётся через Response.server_addr() — это IP origin'а после
    # HTTP-редиректов. Для CDN-сайтов вернёт IP CDN-узла, что и нужно для
    # оценки ст. 18 ч. 5 152-ФЗ (локализация ПДн).
    server_ip: str | None = None


async def fetch_page(
    browser: Browser,
    url: str,
    *,
    timeout_ms: int = 20_000,
    # domcontentloaded быстрее и надёжнее: на SPA (React/Vue) networkidle
    # часто не наступает вообще (фоновые WebSocket/SSE), и мы зависаем до
    # полного timeout_ms × pages. Все факты, которые мы парсим (формы, скрипты,
    # cookie), к moment'у DCL уже на месте.
    wait_until: str = "domcontentloaded",
    user_agent: str = DEFAULT_UA,
    interact_modals: bool = True,
    max_modal_clicks: int = 8,
    modal_wait_ms: int = 3_000,
    # Жёсткий потолок на ВСЮ фазу взаимодействия со страницей. Лимита числа
    # кликов мало: 8 × (клик ~2с + ожидание ~3с + закрытие) — это десятки секунд
    # оверхеда, что при multi-page упирается в SCAN_TIMEOUT_SEC. Бюджет
    # гарантирует ограниченное суммарное время независимо от числа триггеров.
    interact_budget_ms: int = 15_000,
) -> FetchResult:
    context = await browser.new_context(user_agent=user_agent, locale="ru-RU")
    request_urls: list[str] = []
    context.on("request", lambda req: request_urls.append(req.url))

    page = await context.new_page()
    try:
        response = await page.goto(url, timeout=timeout_ms, wait_until=wait_until)
    except PlaywrightError as exc:
        # networkidle часто не наступает на «живых» сайтах — пробуем мягче.
        try:
            response = await page.goto(url, timeout=timeout_ms, wait_until="domcontentloaded")
        except PlaywrightError as exc2:
            await context.close()
            return FetchResult(url=url, final_url=url, status=None, error=str(exc2 or exc))

    # Детерминизм набора страниц на SPA: контент и ССЫЛКИ рендерятся уже ПОСЛЕ
    # domcontentloaded. Без паузы eval_on_selector_all('a[href]') снимает пустой/
    # неполный набор ссылок → BFS упирается в одну страницу → число обойдённых
    # страниц дрожит между прогонами (на vk.com видели 1/8/20). Ждём networkidle
    # ОГРАНИЧЕННО: на «живых» SPA он может не наступить никогда, поэтому короткий
    # best-effort таймаут — он лишь даёт JS дорисовать ссылки, но не подвешивает
    # скан до полного timeout_ms (именно поэтому базовый goto остаётся на DCL).
    try:
        await page.wait_for_load_state("networkidle", timeout=4_000)
    except PlaywrightError:
        pass

    try:
        html = await page.content()
        title = await page.title()
        final_url = page.url
        cookies = await context.cookies()
        links = await page.eval_on_selector_all(
            "a[href]", "els => els.map(e => e.href)"
        )
        status = response.status if response else None
    except PlaywrightError as exc:
        await context.close()
        return FetchResult(url=url, final_url=url, status=None, error=str(exc))

    # IP origin'а. Глотаем любую ошибку — поле опциональное.
    server_ip: str | None = None
    if response is not None:
        try:
            addr = await response.server_addr()
            if addr:
                server_ip = addr.get("ipAddress")
        except PlaywrightError:
            pass

    # Фаза взаимодействия: открываем модальные формы и снимаем их DOM.
    #
    # ВНИМАНИЕ (детерминизм): клики догружают скрипты/виджеты, поэтому набор
    # модальных форм, request_urls и cookie после взаимодействия зависит от
    # тайминга рендера/сети. На сайтах С модалками строгий детерминизм скана
    # (одинаковый CrawlJSON между прогонами) не гарантируется — это осознанный
    # размен «полнота аудита форм» против «битовой воспроизводимости». Для
    # статических сайтов без модалок взаимодействие ничего не открывает и
    # детерминизм сохраняется (критерий приёмки проверялся на таком сайте).
    modal_html: list[str] = []
    if interact_modals:
        try:
            modal_html = await _discover_modal_forms(
                page, max_clicks=max_modal_clicks, wait_ms=modal_wait_ms,
                budget_ms=interact_budget_ms,
            )
        except PlaywrightError:
            pass  # взаимодействие — best-effort, статические факты уже сняты

    # cookie снимаем повторно: модалки/виджеты могли выставить новые.
    try:
        cookies = await context.cookies()
    except PlaywrightError:
        pass

    await context.close()
    return FetchResult(
        url=url,
        final_url=final_url,
        status=status,
        html=html,
        title=title,
        cookies=cookies,
        request_urls=request_urls,
        links=links,
        modal_html=modal_html,
        server_ip=server_ip,
    )


# Селектор появления формы после клика по триггеру.
_MODAL_FORM_SELECTOR = (
    "form, [class*=modal] input, [class*=popup] input, "
    "[class*=modal] textarea, [class*=popup] textarea, [role=dialog] input"
)


async def _discover_modal_forms(page, *, max_clicks: int, wait_ms: int,
                                budget_ms: int = 15_000) -> list[str]:
    """Кликает по кнопкам-триггерам модалок и возвращает HTML-снимки DOM.

    Защита от зацикливания/таймаута: не более max_clicks кликов на страницу,
    общий бюджет времени budget_ms на всю фазу, дедуп триггеров по
    нормализованному тексту, каждый клик в try/except.
    """
    # Кандидаты-триггеры: кнопки, ссылки, role=button и элементы с onclick.
    candidates = await page.query_selector_all(
        "button, a, [role=button], [onclick]"
    )

    snapshots: list[str] = []
    seen_texts: set[str] = set()
    clicks = 0
    deadline = time.monotonic() + budget_ms / 1000

    for el in candidates:
        if clicks >= max_clicks or time.monotonic() >= deadline:
            break
        try:
            raw = (await el.inner_text()) or ""
        except PlaywrightError:
            continue
        text = raw.strip().lower()
        if not text or len(text) > 60:
            continue
        if not any(kw in text for kw in MODAL_TRIGGER_KEYWORDS):
            continue
        if text in seen_texts:
            continue
        seen_texts.add(text)

        try:
            if not await el.is_visible():
                continue
            await el.click(timeout=2_000)
            clicks += 1
        except PlaywrightError:
            continue

        # Ждём появления формы/полей в модалке.
        try:
            await page.wait_for_selector(_MODAL_FORM_SELECTOR, timeout=wait_ms)
        except PlaywrightError:
            pass  # форма могла не появиться — снимок всё равно снимем

        # Детерминизм: после появления формы её поля и сторонние виджеты
        # (reCAPTCHA и т.п.) догружаются асинхронно. Без ожидания сетевого
        # простоя снимок DOM ловит разное состояние между прогонами — дрожат
        # число форм/полей и набор third-party доменов. Ждём networkidle
        # ограниченно: на «живых» виджетах он может не наступить, поэтому
        # best-effort с коротким таймаутом.
        try:
            await page.wait_for_load_state("networkidle", timeout=2_000)
        except PlaywrightError:
            pass

        try:
            snapshots.append(await page.content())
        except PlaywrightError:
            pass

        # Закрываем модалку: Esc, затем клик по крестику/оверлею, если остался.
        try:
            await page.keyboard.press("Escape")
            close = await page.query_selector(
                "[class*=modal] [class*=close], [class*=popup] [class*=close], "
                "[aria-label*=close i], [class*=overlay]"
            )
            if close is not None and await close.is_visible():
                await close.click(timeout=1_000)
        except PlaywrightError:
            pass

    return snapshots
