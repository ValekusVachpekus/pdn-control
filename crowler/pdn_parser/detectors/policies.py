"""Детектор ссылок на политику обработки ПДн, согласия и cookie-политику."""

from __future__ import annotations

from urllib.parse import urljoin

from bs4 import BeautifulSoup

from ..models import PolicyLink
from ..signatures import POLICY_PATTERNS


def detect_policy_links(soup: BeautifulSoup, base_url: str) -> list[PolicyLink]:
    seen: set[str] = set()
    result: list[PolicyLink] = []

    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
            continue
        anchor = a.get_text(" ", strip=True)
        haystack = f"{anchor} {href}".lower()

        for kind, patterns in POLICY_PATTERNS.items():
            if any(p in haystack for p in patterns):
                full = urljoin(base_url, href)
                key = (kind, full)
                if key in seen:
                    continue
                seen.add(key)
                result.append(PolicyLink(url=full, anchor_text=anchor[:200], kind=kind))
                break  # одна ссылка — одна категория (первое совпадение)

    return result
