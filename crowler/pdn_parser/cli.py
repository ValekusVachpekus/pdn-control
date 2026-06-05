"""CLI парсера: python -m pdn_parser <url> [опции].

Запускает обход сайта и печатает JSON-отчёт (envelope schema 1.2) в stdout или
в файл через -o. Это вход для ручной проверки и для интеграции с бэкендом.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys

from .crawler import crawl_site


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="pdn_parser",
        description="Парсер сайтов для предварительного аудита рисков 152-ФЗ.",
    )
    p.add_argument("url", help="URL сайта для проверки (схема не обязательна)")
    p.add_argument("--max-pages", type=int, default=20, help="макс. число страниц (по умолчанию 20)")
    p.add_argument("--max-depth", type=int, default=2, help="макс. глубина обхода (по умолчанию 2)")
    p.add_argument("--ignore-robots", action="store_true", help="не учитывать robots.txt")
    p.add_argument("--no-headless", action="store_true", help="показывать окно браузера")
    p.add_argument("--timeout", type=int, default=20_000, help="таймаут загрузки страницы, мс")
    p.add_argument("--scan-id", help="идентификатор скана (по умолчанию генерится uuid)")
    p.add_argument("--policy-text-to-files", action="store_true",
                   help="сохранять тексты политик в отдельные файлы вместо inline")
    p.add_argument("-o", "--output", help="файл для записи JSON (по умолчанию stdout)")
    p.add_argument("--indent", type=int, default=2, help="отступ JSON (0 — компактно)")
    return p


async def _run(args: argparse.Namespace) -> int:
    output_dir = os.path.dirname(os.path.abspath(args.output)) if args.output else None
    result = await crawl_site(
        args.url,
        requested_url=args.url,
        scan_id=args.scan_id,
        max_pages=args.max_pages,
        max_depth=args.max_depth,
        respect_robots=not args.ignore_robots,
        headless=not args.no_headless,
        page_timeout_ms=args.timeout,
        policy_text_to_files=args.policy_text_to_files,
        output_dir=output_dir,
    )
    payload = json.dumps(result.to_dict(), ensure_ascii=False, indent=args.indent or None)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(payload)
        print(f"Отчёт сохранён: {args.output} "
              f"(страниц: {result.meta.pages_crawled}, статус: {result.meta.status})",
              file=sys.stderr)
    else:
        print(payload)
    return 0


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        return asyncio.run(_run(args))
    except KeyboardInterrupt:
        print("Прервано пользователем", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
