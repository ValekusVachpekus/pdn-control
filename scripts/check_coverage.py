#!/usr/bin/env python3
"""Per-module coverage gate.

`pytest --cov-fail-under` проверяет ТОЛЬКО агрегат по всему прогону, а DoD задачи
(#71) требует порог на КАЖДЫЙ критический модуль. Этот скрипт читает coverage.json
(`coverage json` / `pytest --cov-report=json`) и падает, если хотя бы один из
перечисленных модулей ниже порога.

Использование:
    python check_coverage.py coverage.json --min 30 \\
        app/services/violation_catalog.py app/services/llm_cache.py

Пути модулей должны совпадать с ключами в coverage.json (обычно относительно
каталога, из которого запускался прогон). Печатает таблицу и список критических
модулей; код возврата 1, если какой-то модуль ниже порога или вовсе отсутствует
в отчёте (отсутствие = не покрыт = провал, чтобы переименование не пряталось).
"""

from __future__ import annotations

import argparse
import json
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("coverage_json", help="путь к coverage.json")
    parser.add_argument("--min", type=float, default=30.0,
                        help="минимальный %% покрытия строк на модуль (по умолчанию 30)")
    parser.add_argument("modules", nargs="+",
                        help="пути модулей, как в coverage.json")
    args = parser.parse_args(argv)

    try:
        with open(args.coverage_json, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: не удалось прочитать {args.coverage_json}: {exc}", file=sys.stderr)
        return 2

    files = data.get("files", {})
    # Нормализуем ключи: coverage иногда пишет ./path или абсолютные пути.
    norm = {}
    for key, val in files.items():
        norm[key] = val
        norm[key.lstrip("./")] = val

    failures: list[str] = []
    print(f"Per-module coverage gate (min {args.min:.0f}% line coverage):")
    print(f"{'module':50} {'cover':>7}  status")
    print("-" * 70)
    for mod in args.modules:
        entry = norm.get(mod) or norm.get(mod.lstrip("./"))
        if entry is None:
            print(f"{mod:50} {'n/a':>7}  MISSING")
            failures.append(f"{mod}: отсутствует в coverage.json")
            continue
        pct = float(entry.get("summary", {}).get("percent_covered", 0.0))
        ok = pct >= args.min
        print(f"{mod:50} {pct:6.1f}%  {'OK' if ok else 'FAIL'}")
        if not ok:
            failures.append(f"{mod}: {pct:.1f}% < {args.min:.0f}%")

    print("-" * 70)
    if failures:
        print("\nCoverage gate FAILED:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("\nCoverage gate PASSED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
