"""OAuth 2.0 соц-вход: Яндекс (authorization code) и ВКонтакте (VK ID,
OAuth 2.1 + PKCE).

Провайдер-агностично: чтобы включить провайдера, достаточно задать
client_id/secret в окружении (.env.secret) — код менять не нужно. Сетевые
вызовы — async httpx. Чистые части (сборка authorize-URL, PKCE, парсинг email)
вынесены для юнит-тестов без сети.

Документация:
  Yandex ID — https://yandex.ru/dev/id/doc/ (authorize/token/login.yandex.ru/info)
  VK ID      — https://id.vk.ru/ (OAuth 2.1 + PKCE, /oauth2/auth, /oauth2/user_info)
"""
from __future__ import annotations

import base64
import hashlib
import secrets
from dataclasses import dataclass
from urllib.parse import urlencode

import httpx

from ..config import get_settings


class OAuthError(Exception):
    """Сбой обмена кодом или получения профиля у провайдера."""


@dataclass(frozen=True)
class _Provider:
    name: str
    authorize_url: str
    token_url: str
    userinfo_url: str
    scope: str
    pkce: bool  # VK ID требует PKCE; у Яндекса — обычный code flow с секретом


_PROVIDERS: dict[str, _Provider] = {
    "yandex": _Provider(
        name="yandex",
        authorize_url="https://oauth.yandex.ru/authorize",
        token_url="https://oauth.yandex.ru/token",
        userinfo_url="https://login.yandex.ru/info",
        scope="login:email login:info",
        pkce=False,
    ),
    "vk": _Provider(
        name="vk",
        authorize_url="https://id.vk.ru/authorize",
        token_url="https://id.vk.ru/oauth2/auth",
        userinfo_url="https://id.vk.ru/oauth2/user_info",
        scope="email",
        pkce=True,
    ),
}


def is_supported(provider: str) -> bool:
    return provider in _PROVIDERS


def _creds(provider: str) -> tuple[str, str]:
    s = get_settings()
    return {
        "yandex": (s.oauth_yandex_client_id, s.oauth_yandex_client_secret),
        "vk": (s.oauth_vk_client_id, s.oauth_vk_client_secret),
    }[provider]


def is_configured(provider: str) -> bool:
    """Заданы ли данные провайдера (иначе кнопка входа вернёт ошибку)."""
    return bool(_creds(provider)[0])


def uses_pkce(provider: str) -> bool:
    return _PROVIDERS[provider].pkce


# ── PKCE (RFC 7636) ──────────────────────────────────────────────────────────
def new_code_verifier() -> str:
    return secrets.token_urlsafe(64)


def code_challenge_s256(verifier: str) -> str:
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


def build_authorize_url(
    provider: str, *, redirect_uri: str, state: str, code_challenge: str | None = None
) -> str:
    p = _PROVIDERS[provider]
    params = {
        "response_type": "code",
        "client_id": _creds(provider)[0],
        "redirect_uri": redirect_uri,
        "scope": p.scope,
        "state": state,
    }
    if p.pkce:
        params["code_challenge"] = code_challenge or ""
        params["code_challenge_method"] = "S256"
    return f"{p.authorize_url}?{urlencode(params)}"


async def exchange_code(
    provider: str, *, code: str, redirect_uri: str,
    code_verifier: str | None = None, device_id: str | None = None,
) -> str:
    """Меняет authorization code на access_token. OAuthError при сбое."""
    p = _PROVIDERS[provider]
    cid, secret = _creds(provider)
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": cid,
        "redirect_uri": redirect_uri,
    }
    if p.pkce:
        # VK ID: PKCE вместо секрета; device_id приходит в колбэке провайдера.
        if code_verifier:
            data["code_verifier"] = code_verifier
        if device_id:
            data["device_id"] = device_id
    else:
        data["client_secret"] = secret
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                p.token_url, data=data, headers={"Accept": "application/json"}
            )
            resp.raise_for_status()
            token = (resp.json() or {}).get("access_token")
    except httpx.HTTPError as exc:
        raise OAuthError(f"token exchange failed ({provider}): {exc}") from exc
    if not token:
        raise OAuthError(f"no access_token from {provider}")
    return token


def _yandex_email(data: dict) -> str | None:
    email = data.get("default_email")
    if not email:
        emails = data.get("emails") or []
        email = emails[0] if emails else None
    return email


def _vk_email(data: dict) -> str | None:
    user = data.get("user") or data
    return user.get("email")


async def fetch_profile(provider: str, access_token: str) -> tuple[str, str]:
    """Возвращает (email, provider_user_id). OAuthError, если email не отдан."""
    p = _PROVIDERS[provider]
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            if provider == "yandex":
                resp = await client.get(
                    p.userinfo_url, params={"format": "json"},
                    headers={"Authorization": f"OAuth {access_token}"},
                )
            else:  # vk
                resp = await client.post(
                    p.userinfo_url,
                    data={"access_token": access_token, "client_id": _creds(provider)[0]},
                )
            resp.raise_for_status()
            data = resp.json() or {}
    except httpx.HTTPError as exc:
        raise OAuthError(f"profile fetch failed ({provider}): {exc}") from exc

    if provider == "yandex":
        email, uid = _yandex_email(data), str(data.get("id") or "")
    else:
        user = data.get("user") or data
        email, uid = _vk_email(data), str(user.get("user_id") or user.get("id") or "")
    if not email:
        raise OAuthError(f"{provider} did not return an email")
    return email, uid
