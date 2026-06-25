"""Детерминированное определение страны хостинга по IP через offline GeoIP.

Зачем отдельный модуль, а не «знания» LLM: IP→страна — это задача поиска по
таблице (RIR/BGP-аллокации, миллионы диапазонов). LLM такую таблицу целиком не
держит и на длинном хвосте (мелкие региональные хостеры, дешёвый VPS — где как
раз живёт наша SMB-аудитория) ошибается или гадает, причём недетерминированно.
Цена ошибки максимальна: неверная страна → ложный штраф до 6 млн ₽ за нарушение
локализации ПДн (ст. 18 ч. 5 152-ФЗ). Поэтому страну резолвим детерминированно
из локальной базы MaxMind GeoLite2 — один и тот же IP всегда даёт один результат.

Деградация: если библиотека ``geoip2`` не установлена или базы нет в образе —
модуль возвращает ``server_country=None`` (страну не выдумываем), скан не падает.
Никаких сетевых вызовов на скан: база читается из локального mmdb-файла.

Источник базы — MaxMind GeoLite2 (Country + опционально ASN). Лицензия требует
атрибуции и регулярного обновления; см. ``pdn_parser/data/README.md`` и
``scripts/download_geoip.py``.
"""

from __future__ import annotations

import ipaddress
import os
from dataclasses import asdict, dataclass
from pathlib import Path

from .ssrf import _ip_is_safe

# Имена файлов MaxMind GeoLite2 (как в их официальных архивах).
_COUNTRY_DB = "GeoLite2-Country.mmdb"
_ASN_DB = "GeoLite2-ASN.mmdb"

# Каталог с базами. Переопределяется через GEOIP_DB_DIR; по умолчанию — каталог
# data/ внутри пакета (туда их кладёт download_geoip.py / Dockerfile при сборке).
_DEFAULT_DB_DIR = Path(__file__).resolve().parent / "data"


# ASN крупных CDN/облаков. Если IP принадлежит такому ASN, GeoIP вернёт страну
# узла CDN, а не сервера, где реально лежат ПДн → помечаем результат как CDN,
# чтобы бэк не штрафовал «вслепую». Значение — человекочитаемое имя сети.
CDN_ASNS: dict[int, str] = {
    13335: "Cloudflare",
    209242: "Cloudflare",
    15169: "Google",
    16509: "Amazon (AWS/CloudFront)",
    14618: "Amazon (AWS)",
    54113: "Fastly",
    20940: "Akamai",
    16625: "Akamai",
    12222: "Akamai",
    35994: "Akamai",
    8075: "Microsoft (Azure)",
    60068: "CDN77",
    22822: "Edgio (Limelight)",
    19551: "Incapsula/Imperva",
    13414: "Twitter",
    32934: "Meta (Facebook)",
}

# Статический фолбэк по диапазонам — на случай, когда в образ положили только
# Country-базу (ASN-база опциональна). Список курируемый, крупнейшие CDN; для
# Cloudflare диапазоны публичны и стабильны (cloudflare.com/ips). Обновляется
# вручную — это лишь страховка для пометки CDN, не замена ASN-базе.
_CDN_NETWORK_STRINGS: tuple[tuple[str, str], ...] = (
    # Cloudflare IPv4
    ("173.245.48.0/20", "Cloudflare"),
    ("103.21.244.0/22", "Cloudflare"),
    ("103.22.200.0/22", "Cloudflare"),
    ("103.31.4.0/22", "Cloudflare"),
    ("141.101.64.0/18", "Cloudflare"),
    ("108.162.192.0/18", "Cloudflare"),
    ("190.93.240.0/20", "Cloudflare"),
    ("188.114.96.0/20", "Cloudflare"),
    ("197.234.240.0/22", "Cloudflare"),
    ("198.41.128.0/17", "Cloudflare"),
    ("162.158.0.0/15", "Cloudflare"),
    ("104.16.0.0/13", "Cloudflare"),
    ("104.24.0.0/14", "Cloudflare"),
    ("172.64.0.0/13", "Cloudflare"),
    ("131.0.72.0/22", "Cloudflare"),
    # Cloudflare IPv6
    ("2400:cb00::/32", "Cloudflare"),
    ("2606:4700::/32", "Cloudflare"),
    ("2803:f800::/32", "Cloudflare"),
    ("2405:b500::/32", "Cloudflare"),
    ("2405:8100::/32", "Cloudflare"),
    ("2a06:98c0::/29", "Cloudflare"),
    ("2c0f:f248::/32", "Cloudflare"),
)

_CDN_NETWORKS: tuple[tuple[ipaddress._BaseNetwork, str], ...] = tuple(
    (ipaddress.ip_network(cidr), name) for cidr, name in _CDN_NETWORK_STRINGS
)


@dataclass(frozen=True)
class GeoResult:
    """Факты о хостинге по IP. Только факты — вердикт о локализации выносит бэк.

    ``server_country``       ISO-2 ("RU", "US", …) или None, если не определили.
    ``server_country_source`` "geoip" если страна из базы; None — иначе.
    ``server_is_cdn``        IP принадлежит известному CDN/облаку → страна узла
                             CDN может не совпадать с местом хранения ПДн.
    ``server_country_confidence`` "high" | "low" | "unknown":
        high   — страна из базы и это не CDN;
        low    — страна из базы, но IP за CDN (origin может быть в другой стране);
        unknown — страну определить не удалось.
    ``hosting_provider``     организация-владелец ASN (если есть ASN-база), иначе
                             имя CDN из статического фолбэка, иначе None.
    ``server_asn``           номер автономной системы (если есть ASN-база).
    """

    server_country: str | None = None
    server_country_source: str | None = None
    server_is_cdn: bool = False
    server_country_confidence: str = "unknown"
    hosting_provider: str | None = None
    server_asn: int | None = None

    def as_meta(self) -> dict:
        """Поля для встраивания в ScanMeta/JSON-контракт."""
        return asdict(self)


# Ленивая загрузка ридеров с кэшем на уровне модуля. Сентинел отличает «ещё не
# пробовали открыть» от «пробовали, не вышло (None)» — чтобы не дёргать диск на
# каждый скан, если базы нет.
_UNSET = object()
_country_reader = _UNSET
_asn_reader = _UNSET


def _db_dir() -> Path:
    return Path(os.environ.get("GEOIP_DB_DIR") or _DEFAULT_DB_DIR)


def _open_reader(filename: str):
    """Открывает mmdb-ридер или возвращает None (нет geoip2 / нет файла / битый).

    geoip2.database.Reader держит memory-mapped файл и потокобезопасен на чтение,
    поэтому один общий ридер на процесс — это нормально.
    """
    path = _db_dir() / filename
    if not path.is_file():
        return None
    try:
        import geoip2.database  # импорт ленивый: без базы зависимость не нужна
    except ImportError:
        return None
    try:
        return geoip2.database.Reader(str(path))
    except Exception:
        return None


def _get_country_reader():
    global _country_reader
    if _country_reader is _UNSET:
        _country_reader = _open_reader(_COUNTRY_DB)
    return _country_reader


def _get_asn_reader():
    global _asn_reader
    if _asn_reader is _UNSET:
        _asn_reader = _open_reader(_ASN_DB)
    return _asn_reader


def reset_readers() -> None:
    """Сбросить кэш ридеров (для тестов и смены GEOIP_DB_DIR на лету)."""
    global _country_reader, _asn_reader
    for r in (_country_reader, _asn_reader):
        try:
            if r is not None and r is not _UNSET:
                r.close()
        except Exception:
            pass
    _country_reader = _UNSET
    _asn_reader = _UNSET


def _lookup_country(ip_str: str) -> str | None:
    reader = _get_country_reader()
    if reader is None:
        return None
    try:
        return reader.country(ip_str).country.iso_code or None
    except Exception:
        # AddressNotFoundError и пр. — IP нет в базе, страну не выдумываем.
        return None


def _lookup_asn(ip_str: str) -> tuple[int | None, str | None]:
    reader = _get_asn_reader()
    if reader is None:
        return None, None
    try:
        rec = reader.asn(ip_str)
        return rec.autonomous_system_number, rec.autonomous_system_organization or None
    except Exception:
        return None, None


def _cdn_name_by_network(ip) -> str | None:
    for net, name in _CDN_NETWORKS:
        if ip.version == net.version and ip in net:
            return name
    return None


def resolve_geo(ip_str: str | None) -> GeoResult:
    """Определить страну/CDN по IP сервера. Детерминированно, без сети.

    Пустой / приватный / зарезервированный / непарсящийся IP → страна None
    (источник None): страну не выдумываем — цена ложного штрафа максимальна.
    """
    if not ip_str:
        return GeoResult()
    try:
        ip = ipaddress.ip_address(ip_str.split("%", 1)[0])
    except ValueError:
        return GeoResult()
    # Приватный/служебный адрес (CGNAT, loopback, link-local …) — гео бессмысленно.
    if not _ip_is_safe(ip):
        return GeoResult()

    asn, org = _lookup_asn(str(ip))
    cdn_name = CDN_ASNS.get(asn) if asn is not None else None
    if cdn_name is None:
        cdn_name = _cdn_name_by_network(ip)
    is_cdn = cdn_name is not None

    country = _lookup_country(str(ip))
    source = "geoip" if country else None
    if country:
        confidence = "low" if is_cdn else "high"
    else:
        confidence = "unknown"

    provider = org or (cdn_name if is_cdn else None)

    return GeoResult(
        server_country=country,
        server_country_source=source,
        server_is_cdn=is_cdn,
        server_country_confidence=confidence,
        hosting_provider=provider,
        server_asn=asn,
    )
