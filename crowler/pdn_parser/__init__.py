"""ПДн Контроль — парсер сайтов.

Собирает факты о публичных страницах сайта (формы, cookie, скрипты, политики,
тексты документов, передача данных третьим лицам) и отдаёт их конвертом
CrawlResult (schema 1.2) для дальнейшего rule-based и LLM-анализа.
Юридических выводов не делает. Контракт описан в crowler/CONTRACT.md.
"""

from __future__ import annotations

from importlib import resources

from .crawler import PARSER_VERSION, Crawler, crawl_site
from .models import SCHEMA_VERSION, CrawlResult, PageData

__all__ = [
    "Crawler",
    "crawl_site",
    "CrawlResult",
    "PageData",
    "schema_path",
    "SCHEMA_VERSION",
    "PARSER_VERSION",
]
__version__ = PARSER_VERSION


def schema_path() -> str:
    """Путь к JSON Schema контракта (для валидации/генерации типов на бэке)."""
    with resources.as_file(resources.files(__package__) / "schema.json") as p:
        return str(p)
