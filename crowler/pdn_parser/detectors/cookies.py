"""Детектор cookie-баннера в DOM и классификация выставленных cookie."""

from __future__ import annotations

from bs4 import BeautifulSoup, Tag

from ..models import CookieBanner, CookieInfo
from ..signatures import ACCEPT_WORDS, COOKIE_KEYWORDS, REJECT_WORDS, SETTINGS_WORDS
from ..utils import registrable_domain


def _button_words_present(scope: Tag, words: tuple[str, ...]) -> bool:
    for el in scope.find_all(("button", "a", "input")):
        text = (el.get_text(" ", strip=True) or el.get("value") or "").lower()
        if any(w in text for w in words):
            return True
    return False


def detect_cookie_banner(soup: BeautifulSoup) -> CookieBanner:
    """Ищем блок с упоминанием cookie и кнопками управления.

    Эвристика: берём элементы, чей текст содержит ключевые слова про cookie,
    и выбираем самый компактный (баннеры обычно короткие, в отличие от страницы
    политики целиком).
    """
    candidates: list[tuple[int, Tag]] = []
    for el in soup.find_all(("div", "section", "aside", "footer")):
        text = el.get_text(" ", strip=True).lower()
        if not text or len(text) > 1200:
            continue
        if any(kw in text for kw in COOKIE_KEYWORDS):
            candidates.append((len(text), el))

    if not candidates:
        return CookieBanner(present=False)

    _, banner = min(candidates, key=lambda c: c[0])
    text = banner.get_text(" ", strip=True)
    low = text.lower()
    return CookieBanner(
        present=True,
        full_text=text,
        text_excerpt=text[:400],
        has_accept_button=_button_words_present(banner, ACCEPT_WORDS),
        has_reject_button=_button_words_present(banner, REJECT_WORDS),
        has_settings=_button_words_present(banner, SETTINGS_WORDS),
        matched_keywords=[kw for kw in COOKIE_KEYWORDS if kw in low],
    )


def classify_cookies(raw_cookies: list[dict], page_domain: str) -> list[CookieInfo]:
    """raw_cookies — то, что вернул Playwright context.cookies()."""
    base = registrable_domain(page_domain)
    result: list[CookieInfo] = []
    for c in raw_cookies:
        domain = (c.get("domain") or "").lstrip(".")
        third_party = registrable_domain(domain) != base if domain else False
        result.append(
            CookieInfo(
                name=c.get("name", ""),
                domain=domain,
                third_party=third_party,
                http_only=bool(c.get("httpOnly")),
                secure=bool(c.get("secure")),
                expires=c.get("expires") if c.get("expires", -1) and c.get("expires", -1) > 0 else None,
            )
        )
    return result
