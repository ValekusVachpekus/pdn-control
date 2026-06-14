"""Детектор сторонних скриптов, метрик, CRM-виджетов и пикселей.

Источники сигнала три, и они дополняют друг друга:
  1. теги <script> в DOM (src и инлайн-код);
  2. сетевые запросы, перехваченные Playwright при загрузке страницы
     (ловит трекеры, которые подгружаются динамически и не видны в исходном HTML);
  3. выставленные cookie — для крупных площадок, где аналитика хостится на
     собственном домене (YouTube, VK, Ozon) и по доменам запросов не ловится,
     но характерные cookie (`_ga`, `_ym_uid`, `_fbp` …) выставляются всегда.
"""

from __future__ import annotations

from bs4 import BeautifulSoup

from ..models import TrackerHit
from ..signatures import COOKIE_SIGNATURES, SIGNATURES, Signature
from ..utils import registrable_domain


def _match_signature(sig: Signature, src_urls: list[str], inline_blobs: list[str],
                     request_urls: list[str]) -> list[str]:
    """Возвращает список свидетельств (откуда сработала сигнатура), либо пустой."""
    evidence: list[str] = []

    for url in request_urls:
        if any(d in url for d in sig.domains):
            evidence.append(f"network:{url[:120]}")
            break

    for url in src_urls:
        if any(d in url for d in sig.domains):
            evidence.append(f"src:{url[:120]}")
            break

    # Платформенная телеметрия по характерному ПУТИ запроса (домен любой).
    if sig.paths:
        for url in request_urls:
            if any(p in url for p in sig.paths):
                evidence.append(f"path:{url[:120]}")
                break

    if sig.js_markers:
        for blob in inline_blobs:
            if any(m in blob for m in sig.js_markers):
                evidence.append("inline")
                break

    return evidence


def detect_trackers(
    soup: BeautifulSoup,
    request_urls: list[str],
    cookies: list[dict],
    page_domain: str,
) -> tuple[list[TrackerHit], list[str]]:
    """Возвращает (найденные трекеры, список сторонних доменов)."""
    base = registrable_domain(page_domain)

    src_urls = [s["src"] for s in soup.find_all("script", src=True)]
    inline_blobs = [s.string or "" for s in soup.find_all("script") if not s.get("src")]

    # Хиты копим по имени трекера: один сервис может проявиться и в скриптах, и в
    # cookie — тогда объединяем свидетельства, а не плодим дубли.
    hits: dict[str, TrackerHit] = {}

    for sig in SIGNATURES:
        evidence = _match_signature(sig, src_urls, inline_blobs, request_urls)
        if not evidence:
            continue
        # Трекер опознан по СИГНАТУРЕ (известная платформа), а не по «домен ≠
        # base». third_party оставляем как информативный флаг: ходила ли страница
        # за ресурсом на сторонний домен.
        third_party = bool(sig.domains) and all(
            registrable_domain(_host(d)) != base for d in sig.domains if "." in d
        )
        hits[sig.name] = TrackerHit(
            name=sig.name,
            category=sig.category,
            third_party=third_party,
            cross_border=sig.cross_border,
            evidence=evidence,
        )

    # Детекция по cookie — независимо от домена скрипта.
    cookie_names = [(c.get("name") or "").lower() for c in cookies]
    for csig in COOKIE_SIGNATURES:
        matched = sorted({
            name for name in cookie_names
            if any(name.startswith(p) for p in csig.cookie_prefixes)
        })
        if not matched:
            continue
        evidence = [f"cookie:{n}" for n in matched]
        existing = hits.get(csig.name)
        if existing is not None:
            existing.evidence.extend(evidence)
        else:
            hits[csig.name] = TrackerHit(
                name=csig.name,
                category=csig.category,
                third_party=True,  # cookie-сигнатура = сторонний сервис аналитики
                cross_border=csig.cross_border,
                evidence=evidence,
            )

    # Все сторонние домены, к которым реально ходила страница, — признак
    # потенциальной передачи данных третьим лицам, даже без known-сигнатуры.
    third_party_domains = sorted({
        registrable_domain(_host(u))
        for u in request_urls
        if _host(u) and registrable_domain(_host(u)) != base
    })

    # Детерминированный порядок: хиты по имени, evidence внутри — по строке
    # (иначе порядок пруфов зависит от порядка прихода сетевых запросов).
    result = sorted(hits.values(), key=lambda h: h.name)
    for h in result:
        h.evidence.sort()
    return result, third_party_domains


def _host(url: str) -> str:
    """Грубое извлечение хоста из url или подстроки домена."""
    s = url.split("://", 1)[-1]
    return s.split("/", 1)[0].split("?", 1)[0].lower()
