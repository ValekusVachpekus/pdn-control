"""Тесты детерминированного определения страны хостинга по IP (geoip.py).

Реального .mmdb в репозитории нет (база лицензионная, не коммитится), поэтому
ридеры подменяются фейками, имитирующими API geoip2: так покрываем всю логику
resolve_geo без сети и без бинарной базы. Отдельно проверяем деградацию, когда
базы нет вовсе.
"""

import ipaddress

import pytest

from pdn_parser import geoip
from pdn_parser.geoip import GeoResult, resolve_geo


class _FakeCountryReader:
    """Имитация geoip2 Country Reader: ip → ISO-2 по словарю."""

    def __init__(self, mapping):
        self._mapping = mapping

    def country(self, ip_str):
        iso = self._mapping.get(ip_str)
        if iso is None:
            raise KeyError(ip_str)  # как AddressNotFoundError — ловится в _lookup_country
        return type("R", (), {"country": type("C", (), {"iso_code": iso})()})()


class _FakeASNReader:
    """Имитация geoip2 ASN Reader: ip → (asn, org) по словарю."""

    def __init__(self, mapping):
        self._mapping = mapping

    def asn(self, ip_str):
        pair = self._mapping.get(ip_str)
        if pair is None:
            raise KeyError(ip_str)
        asn, org = pair
        return type("R", (), {
            "autonomous_system_number": asn,
            "autonomous_system_organization": org,
        })()


@pytest.fixture(autouse=True)
def _clean_readers():
    """Каждый тест стартует с чистым кэшем ридеров."""
    geoip.reset_readers()
    yield
    geoip.reset_readers()


def _install(monkeypatch, *, country=None, asn=None):
    monkeypatch.setattr(geoip, "_get_country_reader",
                        lambda: _FakeCountryReader(country) if country is not None else None)
    monkeypatch.setattr(geoip, "_get_asn_reader",
                        lambda: _FakeASNReader(asn) if asn is not None else None)


# ─── базовый кейс: страна из базы, не CDN ────────────────────────────────────

def test_resolves_country_high_confidence(monkeypatch):
    _install(monkeypatch, country={"5.61.23.10": "RU"})
    r = resolve_geo("5.61.23.10")
    assert r.server_country == "RU"
    assert r.server_country_source == "geoip"
    assert r.server_is_cdn is False
    assert r.server_country_confidence == "high"


def test_foreign_country(monkeypatch):
    _install(monkeypatch, country={"8.8.8.8": "US"})
    # 8.8.8.8 — это Google (ASN 15169 в CDN_ASNS), без ASN-базы попадёт ли в CDN?
    # ASN-базы нет, и в статическом списке диапазонов Google нет → не CDN.
    r = resolve_geo("8.8.8.8")
    assert r.server_country == "US"
    assert r.server_country_confidence == "high"


# ─── детерминизм ─────────────────────────────────────────────────────────────

def test_deterministic_same_ip_same_country(monkeypatch):
    _install(monkeypatch, country={"5.61.23.10": "RU"})
    results = {resolve_geo("5.61.23.10").server_country for _ in range(5)}
    assert results == {"RU"}


# ─── приватные / пустые / битые IP → null ────────────────────────────────────

@pytest.mark.parametrize("ip", [None, "", "10.0.0.1", "192.168.1.1", "127.0.0.1",
                                "::1", "169.254.169.254", "100.64.0.1", "not-an-ip"])
def test_private_or_invalid_ip_is_null(monkeypatch, ip):
    # Даже если бы база что-то вернула — приватный/битый IP не должен дать страну.
    _install(monkeypatch, country={"10.0.0.1": "US", "192.168.1.1": "US"})
    r = resolve_geo(ip)
    assert r == GeoResult()
    assert r.server_country is None
    assert r.server_country_source is None
    assert r.server_country_confidence == "unknown"


# ─── CDN по статическому списку диапазонов (без ASN-базы) ─────────────────────

def test_cdn_by_static_network_cloudflare(monkeypatch):
    # 104.16.0.1 ∈ Cloudflare 104.16.0.0/13 → CDN, confidence low.
    _install(monkeypatch, country={"104.16.0.1": "US"})
    r = resolve_geo("104.16.0.1")
    assert r.server_is_cdn is True
    assert r.server_country == "US"
    assert r.server_country_confidence == "low"
    assert r.hosting_provider == "Cloudflare"


# ─── CDN по ASN (с ASN-базой) ────────────────────────────────────────────────

def test_cdn_by_asn(monkeypatch):
    # 1.1.1.1 — публичный, не входит в статический список диапазонов CDN, поэтому
    # CDN определится именно по ASN из (фейковой) ASN-базы.
    _install(monkeypatch,
             country={"1.1.1.1": "DE"},
             asn={"1.1.1.1": (13335, "Cloudflare, Inc.")})
    r = resolve_geo("1.1.1.1")
    assert r.server_is_cdn is True
    assert r.server_asn == 13335
    assert r.hosting_provider == "Cloudflare, Inc."  # имя из ASN-базы предпочтительнее
    assert r.server_country_confidence == "low"


def test_non_cdn_asn_fills_provider(monkeypatch):
    _install(monkeypatch,
             country={"5.61.23.10": "RU"},
             asn={"5.61.23.10": (29076, "Selectel Ltd.")})
    r = resolve_geo("5.61.23.10")
    assert r.server_is_cdn is False
    assert r.server_asn == 29076
    assert r.hosting_provider == "Selectel Ltd."
    assert r.server_country_confidence == "high"


# ─── IP не в базе → страна null, источник null ───────────────────────────────

def test_ip_not_in_db(monkeypatch):
    _install(monkeypatch, country={"5.61.23.10": "RU"})
    r = resolve_geo("9.9.9.9")  # публичный, но в фейк-базе его нет
    assert r.server_country is None
    assert r.server_country_source is None
    assert r.server_country_confidence == "unknown"


# ─── деградация: базы нет вовсе ──────────────────────────────────────────────

def test_graceful_degradation_no_db(monkeypatch):
    monkeypatch.setattr(geoip, "_get_country_reader", lambda: None)
    monkeypatch.setattr(geoip, "_get_asn_reader", lambda: None)
    r = resolve_geo("5.61.23.10")  # публичный IP, но базы нет
    assert r.server_country is None
    assert r.server_country_source is None
    assert r.server_country_confidence == "unknown"


def test_open_reader_missing_file_returns_none(monkeypatch, tmp_path):
    # Нет файла базы в каталоге → ридер None, без исключений.
    monkeypatch.setenv("GEOIP_DB_DIR", str(tmp_path))
    geoip.reset_readers()
    assert geoip._get_country_reader() is None


# ─── as_meta() отдаёт ровно ожидаемые ключи для встраивания в ScanMeta ────────

def test_as_meta_keys(monkeypatch):
    _install(monkeypatch, country={"5.61.23.10": "RU"})
    meta = resolve_geo("5.61.23.10").as_meta()
    assert set(meta) == {
        "server_country", "server_country_source", "server_is_cdn",
        "server_country_confidence", "hosting_provider", "server_asn",
    }
