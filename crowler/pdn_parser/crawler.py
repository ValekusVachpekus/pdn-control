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
from urllib.parse import urlparse
from xml.etree import ElementTree

import httpx
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from . import detectors
from .fetcher import DEFAULT_UA, fetch_page
from .identity import extract_identity
from .models import SCHEMA_VERSION, CrawlResult, PageData, ScanMeta
from .policy_text import fetch_policy_documents
from .summary import build_summary
from .utils import ensure_scheme, iso_now, new_scan_id, normalize_url, same_site

PARSER_VERSION = "0.2.0"


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
    ) -> None:
        self.max_pages = max_pages
        self.max_depth = max_depth
        self.respect_robots = respect_robots
        self.headless = headless
        self.page_timeout_ms = page_timeout_ms
        self.policy_text_to_files = policy_text_to_files
        self.output_dir = output_dir

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

        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=self.headless)
            try:
                while queue and len(pages) < self.max_pages:
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

                # Тексты политик и реквизиты — пока браузер открыт.
                policy_documents = await fetch_policy_documents(
                    browser, pages,
                    to_files=self.policy_text_to_files,
                    output_dir=self.output_dir,
                    timeout_ms=self.page_timeout_ms,
                )
            finally:
                # При Ctrl+C драйвер уже мог умереть — глушим вторичную ошибку закрытия.
                try:
                    await browser.close()
                except Exception:
                    pass

        summary = build_summary(pages)
        identity = extract_identity(page_texts)
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

    async def _process_page(self, browser, url: str, depth: int, base_domain: str):
        """Возвращает (PageData, links, visible_text, server_ip)."""
        fetched = await fetch_page(browser, url, timeout_ms=self.page_timeout_ms)
        if fetched.error:
            return (
                PageData(url=url, final_url=fetched.final_url, status=fetched.status,
                         depth=depth, error=fetched.error),
                [], "", fetched.server_ip,
            )

        soup = BeautifulSoup(fetched.html, "html.parser")
        trackers, third_party_domains = detectors.detect_trackers(
            soup, fetched.request_urls, base_domain
        )
        page = PageData(
            url=url,
            final_url=fetched.final_url,
            status=fetched.status,
            title=fetched.title,
            depth=depth,
            forms=detectors.detect_forms(soup),
            cookies=detectors.classify_cookies(fetched.cookies, base_domain),
            cookie_banner=detectors.detect_cookie_banner(soup),
            trackers=trackers,
            policy_links=detectors.detect_policy_links(soup, fetched.final_url),
            third_party_domains=third_party_domains,
        )
        return page, fetched.links, soup.get_text(" ", strip=True), fetched.server_ip

    @staticmethod
    def _followable(links: list[str], base_domain: str, visited: set[str]) -> list[str]:
        out: list[str] = []
        for link in links or []:
            if not link.startswith(("http://", "https://")):
                continue
            norm = normalize_url(link)
            if norm not in visited and same_site(norm, base_domain):
                out.append(norm)
        return out

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
            async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
                resp = await client.get(robots_url, headers={"User-Agent": DEFAULT_UA})
                if resp.status_code == 200:
                    rp.parse(resp.text.splitlines())
                    return rp
        except httpx.HTTPError:
            pass
        return None

    async def _seed_urls(self, start_url: str, base_domain: str) -> list[str]:
        seeds = [start_url]
        parsed = urlparse(start_url)
        sitemap_url = f"{parsed.scheme}://{parsed.netloc}/sitemap.xml"
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
                resp = await client.get(sitemap_url, headers={"User-Agent": DEFAULT_UA})
                if resp.status_code == 200:
                    seeds.extend(self._parse_sitemap(resp.text, base_domain))
        except (httpx.HTTPError, ElementTree.ParseError):
            pass
        seen: set[str] = set()
        unique = []
        for u in seeds:
            n = normalize_url(u)
            if n not in seen:
                seen.add(n)
                unique.append(n)
        return unique

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


async def crawl_site(start_url: str, *, requested_url: str | None = None,
                     scan_id: str | None = None, **kwargs) -> CrawlResult:
    return await Crawler(**kwargs).crawl(start_url, requested_url=requested_url, scan_id=scan_id)
