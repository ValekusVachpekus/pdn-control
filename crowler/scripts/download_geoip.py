#!/usr/bin/env python3
"""Скачивает offline GeoIP-базы MaxMind GeoLite2 (Country + ASN) в каталог data/.

Документированный метод обновления баз для детерминированного определения страны
хостинга (см. pdn_parser/geoip.py). Никаких внешних зависимостей — только stdlib.

Нужен license key MaxMind (бесплатная регистрация GeoLite2):
    https://www.maxmind.com/en/geolite2/signup

Использование:
    MAXMIND_LICENSE_KEY=xxxxx python scripts/download_geoip.py \\
        --out pdn_parser/data --editions GeoLite2-Country GeoLite2-ASN

Лицензия GeoLite2 требует атрибуции MaxMind — см. pdn_parser/data/README.md.
"""

from __future__ import annotations

import argparse
import io
import os
import sys
import tarfile
import urllib.parse
import urllib.request
from pathlib import Path

_BASE = "https://download.maxmind.com/app/geoip_download"


def _download_edition(edition: str, license_key: str, out_dir: Path) -> Path:
    query = urllib.parse.urlencode(
        {"edition_id": edition, "license_key": license_key, "suffix": "tar.gz"}
    )
    url = f"{_BASE}?{query}"
    print(f"[geoip] скачиваю {edition} …", flush=True)
    with urllib.request.urlopen(url, timeout=120) as resp:
        blob = resp.read()

    # Архив MaxMind: GeoLite2-X_YYYYMMDD/GeoLite2-X.mmdb — берём именно .mmdb.
    with tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz") as tar:
        member = next(
            (m for m in tar.getmembers() if m.name.endswith(f"{edition}.mmdb")), None
        )
        if member is None:
            raise RuntimeError(f"{edition}: .mmdb не найден в архиве")
        src = tar.extractfile(member)
        if src is None:
            raise RuntimeError(f"{edition}: не удалось прочитать .mmdb из архива")
        out_dir.mkdir(parents=True, exist_ok=True)
        dest = out_dir / f"{edition}.mmdb"
        dest.write_bytes(src.read())
    print(f"[geoip] сохранено: {dest} ({dest.stat().st_size} байт)", flush=True)
    return dest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        default=str(Path(__file__).resolve().parents[1] / "pdn_parser" / "data"),
        help="каталог для .mmdb (по умолчанию pdn_parser/data)",
    )
    parser.add_argument(
        "--editions",
        nargs="+",
        default=["GeoLite2-Country", "GeoLite2-ASN"],
        help="какие базы скачать",
    )
    parser.add_argument(
        "--license-key",
        default=os.environ.get("MAXMIND_LICENSE_KEY", ""),
        help="MaxMind license key (или env MAXMIND_LICENSE_KEY)",
    )
    args = parser.parse_args(argv)

    if not args.license_key:
        print(
            "[geoip] не задан MAXMIND_LICENSE_KEY — пропускаю скачивание "
            "(server_country будет null до появления базы).",
            file=sys.stderr,
        )
        return 0

    out_dir = Path(args.out)
    for edition in args.editions:
        _download_edition(edition, args.license_key, out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
