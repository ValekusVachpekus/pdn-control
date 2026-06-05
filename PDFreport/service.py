"""HTTP-микросервис генерации PDF-отчёта.

Принимает JSON по Контракту №2, валидирует, компилирует PDF через Typst и отдаёт
файл. Запуск (из папки PDFreport):

    uv run uvicorn service:app --host 0.0.0.0 --port 8020

Эндпоинты:
    GET  /health  — проверка живости + доступность typst.
    POST /render  — тело = JSON Контракта №2, ответ = application/pdf.
"""

from __future__ import annotations

import logging
import shutil

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response

from models import Report
from renderer import RenderError, TypstNotFound, render_pdf

log = logging.getLogger("pdfreport")

app = FastAPI(
    title="ПДн Контроль — PDF Report",
    description="Микросервис генерации PDF-отчёта из JSON (Контракт №2) через Typst.",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "typst": shutil.which("typst") is not None}


@app.post(
    "/render",
    responses={200: {"content": {"application/pdf": {}}, "description": "PDF-отчёт"}},
)
def render(report: Report) -> Response:
    try:
        pdf = render_pdf(report.model_dump(mode="json", by_alias=True))
    except TypstNotFound as exc:
        log.error("typst unavailable: %s", exc)
        raise HTTPException(status_code=503, detail="typst is not available") from exc
    except RenderError as exc:
        log.error("typst compile failed:\n%s", exc.stderr)
        raise HTTPException(status_code=500, detail="PDF render failed") from exc

    filename = f"report_{report.document_meta.report_id}.pdf"
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )
