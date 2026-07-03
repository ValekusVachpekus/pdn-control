"""Юнит-тесты сервиса аутентификации MVP v2 (bcrypt + JWT).

Ядро Sprint 5 «Auth & Architecture»: хэширование паролей и подпись/проверка JWT.
Чистые функции — ни БД, ни Redis, ни сети. Покрываем корректный путь и границы
безопасности (подмена/просрочка/битый токен), чтобы регрессия в auth ловилась в CI.
"""
from __future__ import annotations

import os
import uuid
from datetime import datetime, timedelta, timezone

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://pdn:pdn@127.0.0.1:5432/pdn")
os.environ["JWT_SECRET"] = "test-secret-test-secret-test-secret"
os.environ.setdefault("LLM_API_KEY", "")

import pytest  # noqa: E402
from jose import JWTError, jwt  # noqa: E402

from app.config import get_settings  # noqa: E402
from app.services.auth import (  # noqa: E402
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


# ─── bcrypt ──────────────────────────────────────────────────────────────────

def test_password_hash_roundtrip():
    h = hash_password("secretpass1")
    assert h != "secretpass1"          # не хранится в открытом виде
    assert verify_password("secretpass1", h) is True
    assert verify_password("wrongpass", h) is False


def test_password_hash_is_salted():
    # Два хэша одного пароля различаются (случайная соль), но оба валидны.
    h1, h2 = hash_password("samepass"), hash_password("samepass")
    assert h1 != h2
    assert verify_password("samepass", h1)
    assert verify_password("samepass", h2)


def test_password_truncated_at_72_bytes():
    # bcrypt игнорирует байты после 72 — проверяем, что усечение согласовано
    # между hash и verify (иначе длинные пароли молча ломали бы вход).
    base = "a" * 72
    h = hash_password(base)
    assert verify_password(base + "EXTRA_IGNORED_TAIL", h) is True


def test_verify_password_malformed_hash_is_false():
    # Битый хэш (например, у OAuth-юзера без пароля) → False, а не исключение.
    assert verify_password("whatever", "not-a-bcrypt-hash") is False


# ─── JWT ─────────────────────────────────────────────────────────────────────

def test_token_roundtrip_returns_user_id():
    uid = uuid.uuid4()
    token = create_access_token(uid)
    assert decode_access_token(token) == uid


def test_tampered_token_rejected():
    token = create_access_token(uuid.uuid4())
    tampered = token[:-2] + ("aa" if token[-2:] != "aa" else "bb")
    with pytest.raises(JWTError):
        decode_access_token(tampered)


def test_token_signed_with_other_secret_rejected():
    uid = uuid.uuid4()
    forged = jwt.encode(
        {"sub": str(uid), "exp": int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp())},
        "some-other-secret-some-other-secret", algorithm="HS256",
    )
    with pytest.raises(JWTError):
        decode_access_token(forged)


def test_expired_token_rejected():
    s = get_settings()
    uid = uuid.uuid4()
    past = datetime.now(timezone.utc) - timedelta(minutes=5)
    expired = jwt.encode(
        {"sub": str(uid), "iat": int(past.timestamp()), "exp": int(past.timestamp())},
        s.jwt_secret, algorithm=s.jwt_algorithm,
    )
    with pytest.raises(JWTError):
        decode_access_token(expired)


def test_token_without_sub_rejected():
    s = get_settings()
    no_sub = jwt.encode(
        {"exp": int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp())},
        s.jwt_secret, algorithm=s.jwt_algorithm,
    )
    with pytest.raises(JWTError):
        decode_access_token(no_sub)


def test_token_with_non_uuid_sub_rejected():
    s = get_settings()
    bad = jwt.encode(
        {"sub": "not-a-uuid",
         "exp": int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp())},
        s.jwt_secret, algorithm=s.jwt_algorithm,
    )
    with pytest.raises(JWTError):
        decode_access_token(bad)
