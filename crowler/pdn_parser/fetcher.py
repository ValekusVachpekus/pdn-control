"""Загрузка страницы через Playwright с перехватом cookie и сетевых запросов.

Каждая страница грузится в свежем browser-контексте: так cookie, выставленные
сайтом, и запросы к третьим лицам отражают ровно один первичный визит
(важно для аудита «что ставится до согласия»).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from playwright.async_api import Browser, Error as PlaywrightError

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
        server_ip=server_ip,
    )
