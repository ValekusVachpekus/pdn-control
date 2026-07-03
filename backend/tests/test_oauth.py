"""Юнит-тесты OAuth-соцвхода (чистые части: PKCE, authorize-URL, парсинг email,
state-store). Сеть/БД не нужны.
"""
from __future__ import annotations

import base64
import hashlib
import os
from urllib.parse import parse_qs, urlparse

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://pdn:pdn@127.0.0.1:5432/pdn")
os.environ.setdefault("JWT_SECRET", "test-test-test-test-test-test-test")
os.environ.setdefault("LLM_API_KEY", "")
os.environ["OAUTH_YANDEX_CLIENT_ID"] = "yandex-cid"
os.environ["OAUTH_YANDEX_CLIENT_SECRET"] = "yandex-secret"
os.environ["OAUTH_VK_CLIENT_ID"] = "vk-cid"

from app.config import get_settings  # noqa: E402

get_settings.cache_clear()  # перечитать settings с заданными OAUTH_* переменными

from app.services import oauth, oauth_state  # noqa: E402


def test_supported_and_configured():
    assert oauth.is_supported("yandex") and oauth.is_supported("vk")
    assert not oauth.is_supported("google")
    assert oauth.is_configured("yandex") is True
    assert oauth.is_configured("vk") is True


def test_pkce_challenge_matches_s256():
    v = oauth.new_code_verifier()
    assert isinstance(v, str) and len(v) >= 43
    ch = oauth.code_challenge_s256(v)
    expected = base64.urlsafe_b64encode(hashlib.sha256(v.encode()).digest()).rstrip(b"=").decode()
    assert ch == expected
    assert "=" not in ch  # base64url без паддинга


def test_yandex_authorize_url_no_pkce():
    url = oauth.build_authorize_url(
        "yandex", redirect_uri="https://x/cb", state="st1", code_challenge=None
    )
    assert url.startswith("https://oauth.yandex.ru/authorize?")
    q = parse_qs(urlparse(url).query)
    assert q["response_type"] == ["code"]
    assert q["client_id"] == ["yandex-cid"]
    assert q["redirect_uri"] == ["https://x/cb"]
    assert q["state"] == ["st1"]
    assert "code_challenge" not in q  # у Яндекса PKCE не используется


def test_vk_authorize_url_has_pkce():
    url = oauth.build_authorize_url(
        "vk", redirect_uri="https://x/cb", state="st2", code_challenge="CH"
    )
    assert url.startswith("https://id.vk.ru/authorize?")
    q = parse_qs(urlparse(url).query)
    assert q["code_challenge"] == ["CH"]
    assert q["code_challenge_method"] == ["S256"]


def test_yandex_email_extraction():
    assert oauth._yandex_email({"default_email": "a@ya.ru"}) == "a@ya.ru"
    assert oauth._yandex_email({"emails": ["b@ya.ru", "c@ya.ru"]}) == "b@ya.ru"
    assert oauth._yandex_email({"login": "x"}) is None


def test_vk_email_extraction():
    assert oauth._vk_email({"user": {"email": "u@vk.com", "user_id": 42}}) == "u@vk.com"
    assert oauth._vk_email({"email": "top@vk.com"}) == "top@vk.com"
    assert oauth._vk_email({"user": {"user_id": 1}}) is None


class _FakeRedis:
    def __init__(self) -> None:
        self.store: dict[str, str] = {}

    def set(self, key: str, value: str, ex: int | None = None) -> bool:
        self.store[key] = value
        return True

    def get(self, key: str) -> str | None:
        return self.store.get(key)

    def delete(self, key: str) -> int:
        return 1 if self.store.pop(key, None) is not None else 0


def test_state_store_roundtrip_and_single_use():
    c = _FakeRedis()
    payload = {"provider": "vk", "consent": True, "code_verifier": "v"}
    oauth_state.save_state("s1", payload, client=c)
    assert oauth_state.pop_state("s1", client=c) == payload
    # повторное извлечение — уже нет (одноразовый)
    assert oauth_state.pop_state("s1", client=c) is None
    # неизвестный state
    assert oauth_state.pop_state("nope", client=c) is None
