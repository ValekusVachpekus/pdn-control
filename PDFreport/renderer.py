"""Рендеринг PDF из JSON через Typst.

Паттерн: на каждый запрос — изолированная рабочая папка, куда кладём data.json и
шаблон, и компилируем с `--root` на эту папку. Так Typst не выходит за пределы
песочницы и не ломается на параллельных запросах.
"""

from __future__ import annotations

import json
import pathlib
import shutil
import subprocess
import tempfile

TEMPLATE = pathlib.Path(__file__).parent / "template.typ"


class TypstNotFound(RuntimeError):
    """Бинарь `typst` не найден в PATH."""


class RenderError(RuntimeError):
    """Typst завершился с ошибкой компиляции."""

    def __init__(self, message: str, stderr: str = "") -> None:
        super().__init__(message)
        self.stderr = stderr


def render_pdf(report: dict) -> bytes:
    """`report` — dict по Контракту №2. Возвращает байты PDF.

    Поднимает :class:`TypstNotFound`, если бинарь недоступен, и
    :class:`RenderError` при ошибке компиляции шаблона.
    """
    if shutil.which("typst") is None:
        raise TypstNotFound("typst binary not found in PATH")

    with tempfile.TemporaryDirectory() as tmp:
        job = pathlib.Path(tmp)
        (job / "data.json").write_text(
            json.dumps(report, ensure_ascii=False), encoding="utf-8"
        )
        shutil.copy(TEMPLATE, job / "template.typ")
        out = job / "report.pdf"
        try:
            subprocess.run(
                ["typst", "compile", "--root", str(job),
                 str(job / "template.typ"), str(out)],
                check=True, capture_output=True, text=True,
            )
        except subprocess.CalledProcessError as exc:
            raise RenderError("typst compile failed", stderr=exc.stderr) from exc
        return out.read_bytes()
