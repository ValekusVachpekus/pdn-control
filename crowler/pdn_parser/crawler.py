"""Crawler публичных страниц + сборка отчёта (envelope schema 1.2).

Алгоритм:
  1. читаем robots.txt (по умолчанию уважаем Disallow);
  2. берём seed-ссылки из sitemap.xml + стартовый URL;
  3. обходим в ширину в пределах одного сайта, ограничивая глубину и число страниц;
  4. каждую страницу рендерим Playwright и прогоняем через детекторы;
  5. скачиваем тексты найденных политик, извлекаем реквизиты, агрегируем summary.
"""

from __future__ import annotations

import time
import urllib.robotparser
from collections import deque
from urllib.parse import urljoin, urlparse
from xml.etree import ElementTree

import httpx
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from . import detectors
from .fetcher import DEFAULT_UA, fetch_page
from .ssrf import SSRFGuard
from .identity import extract_identity
from .models import SCHEMA_VERSION, CrawlResult, PageData, ScanMeta
from .policy_text import fetch_policy_documents
from .summary import build_summary
from .utils import ensure_scheme, iso_now, new_scan_id, normalize_url, same_site

PARSER_VERSION = "0.2.0"


class _SSRFBlocked(Exception):
    """robots.txt/sitemap.xml ведут (или редиректят) на внутренний адрес."""


async def _guarded_get(url: str, *, headers: dict | None = None,
                       timeout: float = 10, max_redirects: int = 3) -> httpx.Response:
    """httpx GET с анти-SSRF проверкой исходного URL И КАЖДОГО редирект-хопа.

    robots.txt/sitemap.xml грузятся напрямую через httpx (не через Playwright),
    поэтому сетевой перехват SSRFGuard на них не распространяется. Без этой
    обёртки внутренний адрес — или публичный URL/сокращатель, 30x-редиректящий
    на внутренний, — обходит защиту краулера. follow_redirects=False + ручной
    цикл: каждый Location резолвится и валидируется ДО следующего запроса.
    """
    guard = SSRFGuard()
    async with httpx.AsyncClient(follow_redirects=False, timeout=timeout) as client:
        current = url
        for _ in range(max_redirects + 1):
            verdict = await guard.check_url(current)
            if not verdict.allowed:
                raise _SSRFBlocked(verdict.reason)
            resp = await client.get(current, headers=headers)
            if resp.is_redirect and resp.headers.get("location"):
                current = urljoin(current, resp.headers["location"])
                continue
            return resp
    raise _SSRFBlocked("слишком много редиректов")


class Crawler:
    def __init__(
        self,
        *,
        max_pages: int = 20,
        max_depth: int = 2,
        respect_robots: bool = True,
        headless: bool = True,
        page_timeout_ms: int = 20_000,
        policy_text_to_files: bool = False,
        output_dir: str | None = None,
        interact_modals: bool = True,
        max_modal_clicks: int = 8,
        interact_budget_ms: int = 15_000,
        # Мягкий бюджет времени на ВЕСЬ обход, сек. При его исчерпании цикл
        # перестаёт добирать страницы и финализирует то, что собрал, вместо
        # того чтобы упереться в жёсткий SCAN_TIMEOUT_SEC и упасть с 504 без
        # результата. None = без бюджета (CLI). Backend передаёт значение ниже
        # SCAN_TIMEOUT_SEC, чтобы остановиться заранее.
        time_budget_sec: float | None = None,
    ) -> None:
        self.max_pages = max_pages
        self.max_depth = max_depth
        self.respect_robots = respect_robots
        self.headless = headless
        self.page_timeout_ms = page_timeout_ms
        self.policy_text_to_files = policy_text_to_files
        self.output_dir = output_dir
        self.interact_modals = interact_modals
        self.max_modal_clicks = max_modal_clicks
        self.interact_budget_ms = interact_budget_ms
        self.time_budget_sec = time_budget_sec

    async def crawl(self, start_url: str, *, requested_url: str | None = None,
                    scan_id: str | None = None) -> CrawlResult:
        requested_url = requested_url or start_url
        start_url = normalize_url(ensure_scheme(start_url))
        base_domain = urlparse(start_url).hostname or ""
        started_at = iso_now()
        t0 = time.monotonic()

        pages: list[PageData] = []
        page_texts: list[str] = []
        errors: list[str] = []
        policy_documents = []

        robots = await self._load_robots(start_url) if self.respect_robots else None
        seeds = await self._seed_urls(start_url, base_domain)

        queue: deque[tuple[str, int]] = deque((u, 0) for u in seeds)
        visited: set[str] = set()
        # IP origin'а первой успешно загруженной страницы — кладём в meta.server_ip.
        # Для оценки ст. 18 ч. 5 152-ФЗ важен именно origin сайта, а не его
        # сторонних ресурсов. Дальнейшие страницы переписать значение не могут.
        start_server_ip: str | None = None

        # На дозагрузку текстов политик (после цикла) резервируем часть бюджета —
        # она тоже грузит до _MAX_DOCS страниц и не должна выталкивать скан за
        # SCAN_TIMEOUT_SEC. Резерв адаптивный: не больше четверти бюджета, чтобы
        # при малом бюджете обход не обнулялся (loop_budget не уходит в минус).
        loop_budget = None
        if self.time_budget_sec is not None:
            reserve = min(45.0, self.time_budget_sec * 0.25)
            loop_budget = self.time_budget_sec - reserve

        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=self.headless)
            try:
                while queue and len(pages) < self.max_pages:
                    # Мягкая остановка по времени: возвращаем партиал, а не падаем
                    # по жёсткому таймауту. Срабатывает только на патологически
                    # тяжёлых сайтах; обычные укладываются и остаются детерминированы.
                    if loop_budget is not None and (time.monotonic() - t0) > loop_budget:
                        errors.append(
                            f"бюджет времени обхода исчерпан ({loop_budget:.0f}c), "
                            f"собрано {len(pages)} страниц"
                        )
                        break
                    url, depth = queue.popleft()
                    norm = normalize_url(url)
                    if norm in visited or depth > self.max_depth:
                        continue
                    if not same_site(norm, base_domain):
                        continue
                    if robots is not None and not robots.can_fetch(DEFAULT_UA, norm):
                        errors.append(f"robots.txt запрещает: {norm}")
                        continue
                    visited.add(norm)

                    page_data, links, text, page_server_ip = await self._process_page(
                        browser, norm, depth, base_domain
                    )
                    if start_server_ip is None and page_server_ip:
                        start_server_ip = page_server_ip
                    pages.append(page_data)
                    if text:
                        page_texts.append(text)

                    if page_data.error is None and depth < self.max_depth:
                        for link in self._followable(links, base_domain, visited):
                            queue.append((link, depth + 1))

                # Детерминированный порядок страниц на выходе: при упоре в
                # max_pages набор обойдённых страниц уже одинаков (BFS отсортирован),
                # а сортировка по url убирает зависимость порядка pages[] и
                # производных (trackers.found_on) от тайминга загрузки.
                pages.sort(key=lambda p: p.url)

                # Тексты политик и реквизиты — пока браузер открыт.
                policy_deadline = (
                    t0 + self.time_budget_sec
                    if self.time_budget_sec is not None else None
                )
                policy_documents = await fetch_policy_documents(
                    browser, pages,
                    to_files=self.policy_text_to_files,
                    output_dir=self.output_dir,
                    timeout_ms=self.page_timeout_ms,
                    deadline=policy_deadline,
                )
                policy_documents = sorted(policy_documents, key=lambda d: d.url)
            finally:
                # При Ctrl+C драйвер уже мог умереть — глушим вторичную ошибку закрытия.
                try:
                    await browser.close()
                except Exception:
                    pass

        summary = build_summary(pages)
        # Реквизиты ищем и в видимом тексте страниц, И в тексте политик/согласий:
        # оператор почти всегда назван в политике (ИНН/ОГРН/юр-название), даже
        # если в футере его нет. Это резко снижает ложное «оператор не определён».
        policy_texts = [
            d.extracted_text for d in policy_documents
            if getattr(d, "extracted_text", None)
        ]
        identity = extract_identity(page_texts + policy_texts)
        status = self._status(pages, errors)
        meta = ScanMeta(
            scan_id=scan_id or new_scan_id(),
            parser_version=PARSER_VERSION,
            requested_url=requested_url,
            start_url=start_url,
            base_domain=base_domain,
            started_at=started_at,
            finished_at=iso_now(),
            duration_ms=int((time.monotonic() - t0) * 1000),
            status=status,
            config={
                "max_pages": self.max_pages,
                "max_depth": self.max_depth,
                "respect_robots": self.respect_robots,
                "headless": self.headless,
                "page_timeout_ms": self.page_timeout_ms,
                "interact_modals": self.interact_modals,
                "max_modal_clicks": self.max_modal_clicks,
                "interact_budget_ms": self.interact_budget_ms,
            },
            robots_respected=self.respect_robots,
            pages_requested_limit=self.max_pages,
            pages_crawled=len(pages),
            errors=errors,
            server_ip=start_server_ip,
        )
        return CrawlResult(
            meta=meta,
            summary=summary,
            site_identity=identity,
            policy_documents=policy_documents,
            pages=pages,
            schema_version=SCHEMA_VERSION,
        )

    async def _fetch_with_retry(self, browser, url: str):
        """Загрузка с одним ретраем по таймауту — убирает дивергенцию из-за сетевых сбоев."""
        fetched = await fetch_page(
            browser, url, timeout_ms=self.page_timeout_ms,
            interact_modals=self.interact_modals, max_modal_clicks=self.max_modal_clicks,
            interact_budget_ms=self.interact_budget_ms,
        )
        if fetched.error and "imeout" in fetched.error:
            fetched = await fetch_page(
                browser, url, timeout_ms=self.page_timeout_ms,
                interact_modals=self.interact_modals, max_modal_clicks=self.max_modal_clicks,
                interact_budget_ms=self.interact_budget_ms,
            )
        return fetched

    async def _process_page(self, browser, url: str, depth: int, base_domain: str):
        """Возвращает (PageData, links, visible_text, server_ip)."""
        fetched = await self._fetch_with_retry(browser, url)
        if fetched.error:
            return (
                PageData(url=url, final_url=fetched.final_url, status=fetched.status,
                         depth=depth, error=fetched.error),
                [], "", fetched.server_ip,
            )

        soup = BeautifulSoup(fetched.html, "html.parser")
        trackers, third_party_domains = detectors.detect_trackers(
            soup, fetched.request_urls, fetched.cookies, base_domain
        )

        # Статические формы + формы из модалок (каждый снимок DOM после клика),
        # с дедупом по составу полей + action: одна форма часто открывается
        # несколькими кнопками.
        forms = detectors.detect_forms(soup)
        for snapshot in fetched.modal_html:
            forms.extend(detectors.detect_forms(BeautifulSoup(snapshot, "html.parser")))
        forms = _dedupe_forms(forms)

        page = PageData(
            url=url,
            final_url=fetched.final_url,
            status=fetched.status,
            title=fetched.title,
            depth=depth,
            forms=forms,
            cookies=detectors.classify_cookies(fetched.cookies, base_domain),
            cookie_banner=detectors.detect_cookie_banner(soup),
            trackers=trackers,
            policy_links=detectors.detect_policy_links(soup, fetched.final_url),
            third_party_domains=third_party_domains,
        )
        return page, fetched.links, soup.get_text(" ", strip=True), fetched.server_ip

    @staticmethod
    def _followable(links: list[str], base_domain: str, visited: set[str]) -> list[str]:
        # Дедуп + сортировка по URL — детерминированный порядок постановки в
        # очередь BFS. Без этого порядок зависит от расположения ссылок в DOM,
        # и при упоре в max_pages два скана отбирают разные страницы → разный
        # CrawlJSON → разная оценка LLM. Сортировка делает выбор страниц
        # воспроизводимым для статических сайтов.
        out: set[str] = set()
        for link in links or []:
            if not link.startswith(("http://", "https://")):
                continue
            norm = normalize_url(link)
            if norm not in visited and same_site(norm, base_domain):
                out.add(norm)
        return sorted(out)

    @staticmethod
    def _status(pages: list[PageData], errors: list[str]) -> str:
        if not pages or all(p.error for p in pages):
            return "failed"
        if errors or any(p.error for p in pages):
            return "partial"
        return "ok"

    async def _load_robots(self, start_url: str):
        parsed = urlparse(start_url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        rp = urllib.robotparser.RobotFileParser()
        try:
            resp = await _guarded_get(robots_url, headers={"User-Agent": DEFAULT_UA})
            if resp.status_code == 200:
                rp.parse(resp.text.splitlines())
                return rp
        except (httpx.HTTPError, _SSRFBlocked):
            pass
        return None

    async def _seed_urls(self, start_url: str, base_domain: str) -> list[str]:
        seeds = [start_url]
        parsed = urlparse(start_url)
        sitemap_url = f"{parsed.scheme}://{parsed.netloc}/sitemap.xml"
        try:
            resp = await _guarded_get(sitemap_url, headers={"User-Agent": DEFAULT_UA})
            if resp.status_code == 200:
                seeds.extend(self._parse_sitemap(resp.text, base_domain))
        except (httpx.HTTPError, ElementTree.ParseError, _SSRFBlocked):
            pass
        # Стартовая страница ВСЕГДА первая (с неё снимаем server_ip и она
        # приоритетна для обхода). Остальные seed'ы из sitemap сортируем —
        # детерминированный порядок обхода между сканами.
        start_norm = normalize_url(start_url)
        seen: set[str] = {start_norm}
        rest: list[str] = []
        for u in seeds:
            n = normalize_url(u)
            if n not in seen:
                seen.add(n)
                rest.append(n)
        return [start_norm] + sorted(rest)

    @staticmethod
    def _parse_sitemap(xml_text: str, base_domain: str) -> list[str]:
        urls: list[str] = []
        try:
            root = ElementTree.fromstring(xml_text)
        except ElementTree.ParseError:
            return urls
        for loc in root.iter():
            if loc.tag.endswith("loc") and loc.text:
                url = loc.text.strip()
                if same_site(url, base_domain):
                    urls.append(url)
        return urls


def _form_key(f):
    return (f.action or "", tuple(sorted((fld.name or "") for fld in f.fields)),
            tuple(sorted(k.value for k in f.pii_kinds)))


def _dedupe_forms(forms):
    """Дедуп форм по (action, состав полей). Одна форма часто открывается
    несколькими кнопками-триггерами.

    Сначала дедуп с сохранением порядка (оставляем ПЕРВУЮ — статическая форма
    идёт раньше модальной и предпочтительнее), затем сортировка по ключу для
    детерминированного порядка выдачи между прогонами."""
    seen: set[tuple] = set()
    out = []
    for f in forms:
        key = _form_key(f)
        if key in seen:
            continue
        seen.add(key)
        out.append(f)
    out.sort(key=_form_key)
    return out


async def crawl_site(start_url: str, *, requested_url: str | None = None,
                     scan_id: str | None = None, **kwargs) -> CrawlResult:
    return await Crawler(**kwargs).crawl(start_url, requested_url=requested_url, scan_id=scan_id)
