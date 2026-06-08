"""Клиент к PDF-микросервису (PDFreport, порт 8020)."""
from __future__ import annotations

import httpx

from ..config import get_settings


class PdfError(RuntimeError):
    pass


async def render_pdf(report_json: dict) -> bytes:
    s = get_settings()
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
            resp = await client.post(f"{s.pdfreport_url}/render", json=report_json)
            resp.raise_for_status()
            return resp.content
    except httpx.HTTPStatusError as e:
        raise PdfError(f"pdf {e.response.status_code}: {e.response.text[:300]}") from e
    except httpx.HTTPError as e:
        raise PdfError(f"pdf transport error: {e}") from e
