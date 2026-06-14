"""Скачивание и очистка текста документов (политики/согласия/оферты) для LLM.

После обхода собираем уникальные URL из policy_links всех страниц, заходим на
каждый через уже открытый Playwright-браузер и извлекаем чистый текст.
"""

from __future__ import annotations

import os
import time

from bs4 import BeautifulSoup

from .fetcher import fetch_page
from .models import PageData, PolicyDocument

_MAX_CHARS = 50_000          # лимит на документ, чтобы не раздувать JSON
_MAX_DOCS = 10               # сколько документов максимум скачиваем
_STRIP_TAGS = ("script", "style", "noscript", "nav", "header", "footer", "svg")


def _clean_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(_STRIP_TAGS):
        tag.decompose()
    main = soup.find("main") or soup.body or soup
    return main.get_text(" ", strip=True)


def _collect_policy_urls(pages: list[PageData]) -> dict[str, str]:
    """Уникальные URL документов -> kind (первый встреченный)."""
    urls: dict[str, str] = {}
    for page in pages:
        for link in page.policy_links:
            if link.url.startswith(("http://", "https://")) and link.url not in urls:
                urls[link.url] = link.kind
    return urls


async def fetch_policy_documents(
    browser,
    pages: list[PageData],
    *,
    to_files: bool = False,
    output_dir: str | None = None,
    timeout_ms: int = 20_000,
    # Дедлайн (time.monotonic), после которого новые документы не грузим — чтобы
    # фаза дозагрузки политик не вытолкнула скан за SCAN_TIMEOUT_SEC. None = без
    # ограничения по времени.
    deadline: float | None = None,
) -> list[PolicyDocument]:
    urls = _collect_policy_urls(pages)
    docs: list[PolicyDocument] = []

    for idx, (url, kind) in enumerate(list(urls.items())[:_MAX_DOCS]):
        if deadline is not None and time.monotonic() > deadline:
            break
        fetched = await fetch_page(browser, url, timeout_ms=timeout_ms,
                                   wait_until="domcontentloaded", interact_modals=False)
        if fetched.error or not fetched.html:
            docs.append(PolicyDocument(url=url, kind=kind, fetch_status=fetched.status))
            continue

        text = _clean_text(fetched.html)
        truncated = len(text) > _MAX_CHARS
        if truncated:
            text = text[:_MAX_CHARS]
        word_count = len(text.split())

        doc = PolicyDocument(
            url=url, kind=kind, fetch_status=fetched.status,
            word_count=word_count, truncated=truncated,
        )
        if to_files:
            path = os.path.join(output_dir or ".", f"policy_{idx}.txt")
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(text)
            doc.text_path = path
        else:
            doc.extracted_text = text
        docs.append(doc)

    return docs
