"""Клиент к микросервису парсера (crowler, порт 8010)."""
from __future__ import annotations

import httpx

from ..config import get_settings


class CrawlerError(RuntimeError):
    pass


def scan_site_sync(url: str, *, max_pages: int, max_depth: int = 2, timeout_sec: int = 360) -> dict:
    """Синхронный вызов — для Celery-таска (он работает в обычном sync-контексте)."""
    s = get_settings()
    try:
        with httpx.Client(timeout=httpx.Timeout(timeout_sec)) as client:
            resp = client.post(
                f"{s.crawler_url}/scan",
                json={"url": url, "max_pages": max_pages, "max_depth": max_depth},
            )
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPStatusError as e:
        raise CrawlerError(f"crawler {e.response.status_code}: {e.response.text[:300]}") from e
    except httpx.HTTPError as e:
        raise CrawlerError(f"crawler transport error: {e}") from e
