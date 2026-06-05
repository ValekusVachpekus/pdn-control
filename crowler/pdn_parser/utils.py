"""Мелкие хелперы: нормализация URL, registrable-домен, проверка домена."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from urllib.parse import urldefrag, urlparse, urlunparse


def iso_now() -> str:
    """Текущее время в ISO-8601, UTC, с суффиксом Z."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def new_scan_id() -> str:
    return str(uuid.uuid4())

# Публичные суффиксы второго уровня, которые встречаются у рунета и не только.
# Не полный Public Suffix List — для точности можно подключить tldextract,
# но для MVP этого набора достаточно.
_TWO_LEVEL_SUFFIXES = {
    "co.uk", "org.uk", "com.ru", "net.ru", "org.ru", "com.ua", "co.il",
    "com.tr", "com.br", "co.jp", "msk.ru", "spb.ru",
}


def registrable_domain(host: str) -> str:
    """Возвращает регистрируемый домен (example.com из www.shop.example.com)."""
    host = (host or "").strip().lower().rstrip(".")
    if not host or ":" in host and host.replace(":", "").isdigit():
        return host
    host = host.split(":", 1)[0]  # отрезаем порт
    labels = host.split(".")
    if len(labels) <= 2:
        return host
    last_two = ".".join(labels[-2:])
    last_three = ".".join(labels[-3:])
    if last_two in _TWO_LEVEL_SUFFIXES:
        return last_three
    return last_two


def same_site(url: str, base_domain: str) -> bool:
    host = urlparse(url).hostname or ""
    return registrable_domain(host) == registrable_domain(base_domain)


def normalize_url(url: str) -> str:
    """Убираем фрагмент (#...) и нормализуем пустой путь до '/'."""
    url, _ = urldefrag(url)
    parts = urlparse(url)
    path = parts.path or "/"
    # отбрасываем завершающий слэш, кроме корня, чтобы не плодить дубли
    if len(path) > 1 and path.endswith("/"):
        path = path.rstrip("/")
    return urlunparse((parts.scheme, parts.netloc, path, parts.params, parts.query, ""))


def ensure_scheme(url: str) -> str:
    if not urlparse(url).scheme:
        return "https://" + url
    return url
