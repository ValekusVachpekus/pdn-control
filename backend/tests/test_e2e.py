"""End-to-end API проверка на реальном Postgres + Redis.

Перед запуском подняты контейнеры:
    docker run -d --name pdn-pg-test    -e POSTGRES_USER=pdn -e POSTGRES_PASSWORD=pdn \\
        -e POSTGRES_DB=pdn -p 55432:5432 postgres:16-alpine
    docker run -d --name pdn-redis-test -p 56379:6379 redis:7-alpine

Что покрываем:
  - регистрация / логин;
  - постановка проверки и работа Celery-таска (eager, crawler замокан);
  - получение готового JSON-отчёта (Контракт №2);
  - PDF 402 для free-тарифа;
  - чужой отчёт = 404;
  - валидация URL отсекает мусор/инъекции.
"""
from __future__ import annotations

import os
import subprocess
import uuid
from unittest.mock import patch

# Перед импортом приложения подменяем env под тестовые контейнеры.
os.environ["DATABASE_URL"] = "postgresql+asyncpg://pdn:pdn@127.0.0.1:55432/pdn"
os.environ["JWT_SECRET"] = "test-test-test-test-test-test-test"
os.environ["CELERY_BROKER_URL"] = "memory://"
os.environ["CELERY_RESULT_BACKEND"] = "cache+memory://"
os.environ["CRAWLER_URL"] = "http://unused"

from app import config as _config  # noqa: E402
_config.get_settings.cache_clear()

from app.main import app  # noqa: E402
from app.workers.celery_app import celery_app  # noqa: E402
from app.workers import tasks as _tasks  # noqa: E402, F401

# Celery в синхронном режиме — таск исполняется в том же процессе и в той же транзакции.
celery_app.conf.task_always_eager = True
celery_app.conf.task_eager_propagates = True


SAMPLE_CRAWL = {
    "meta": {
        "requested_url": "example.ru",
        "start_url": "https://example.ru/",
        "base_domain": "example.ru",
        "duration_ms": 5000,
        "pages_crawled": 2,
        "parser_version": "test",
    },
    "summary": {
        "has_privacy_policy": False,
        "privacy_policy_urls": [],
        "has_cookie_banner": False,
        "cookie_banner_has_reject": False,
        "forms_with_prechecked_consent": 0,
        "forms_pii_without_consent": 1,
        "has_cross_border_transfer": False,
        "third_party_domain_count": 0,
        "third_party_domains": [],
        "trackers": [],
    },
    "site_identity": {
        "legal_name_hints": [], "inn": [], "ogrn": [],
        "contact_emails": [], "contact_phones": [],
    },
    "policy_documents": [],
    "pages": [{
        "url": "https://example.ru/",
        "forms": [{
            "action": "/x", "pii_kinds": ["name"],
            "fields": [{"name": "n"}], "consent_checkboxes": [],
        }],
    }],
}


def _run_migrations():
    """Сносим старую схему и накатываем чистый upgrade head."""
    env = os.environ.copy()
    # alembic.ini лежит на уровень выше tests/
    cwd = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    import sys as _sys
    subprocess.run(
        [_sys.executable, "-m", "alembic", "downgrade", "base"],
        cwd=cwd, env=env, check=False, capture_output=True,
    )
    res = subprocess.run(
        [_sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=cwd, env=env, capture_output=True, text=True,
    )
    if res.returncode != 0:
        raise RuntimeError(f"alembic upgrade failed:\n{res.stdout}\n{res.stderr}")


def _fake_scan_site_sync(url, *, max_pages, **kw):
    sample = dict(SAMPLE_CRAWL)
    sample["meta"] = dict(sample["meta"], requested_url=url)
    return sample


async def _run_flow():
    import httpx
    from httpx import ASGITransport

    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Health
        r = await client.get("/api/health")
        assert r.status_code == 200

        # Register
        email = f"u{uuid.uuid4().hex[:10]}@example.com"
        r = await client.post("/api/auth/register",
                              json={"email": email, "password": "secretpass1"})
        assert r.status_code == 201, r.text
        token = r.json()["token"]
        auth = {"Authorization": f"Bearer {token}"}
        assert r.json()["user"]["plan"] == "free"

        # Повторная регистрация → 409
        r = await client.post("/api/auth/register",
                              json={"email": email, "password": "secretpass1"})
        assert r.status_code == 409, r.text

        # Логин
        r = await client.post("/api/auth/login",
                              json={"email": email, "password": "secretpass1"})
        assert r.status_code == 200 and r.json()["token"]

        # Неверный пароль → 401
        r = await client.post("/api/auth/login",
                              json={"email": email, "password": "wrongpass"})
        assert r.status_code == 401

        # Плэны без авторизации
        plans = (await client.get("/api/billing/plans")).json()
        assert {p["id"] for p in plans} == {"free", "pro", "team"}

        # Валидация URL: мусор отсекается
        r = await client.post("/api/scans",
                              json={"url": "example.ru'; DROP TABLE users--"}, headers=auth)
        assert r.status_code == 422, r.text
        r = await client.post("/api/scans",
                              json={"url": "http://localhost"}, headers=auth)
        assert r.status_code == 422

        # Сабмит проверки (парсер замокан)
        with patch("app.workers.tasks.scan_site_sync", side_effect=_fake_scan_site_sync):
            r = await client.post("/api/scans", json={"url": "example.ru"}, headers=auth)
        assert r.status_code == 201, r.text
        report_id = r.json()["report_id"]

        # Статус — done (eager)
        r = await client.get(f"/api/scans/{report_id}/status", headers=auth)
        assert r.status_code == 200, r.text
        assert r.json()["status"] == "done"

        # Отчёт
        r = await client.get(f"/api/reports/{report_id}", headers=auth)
        assert r.status_code == 200, r.text
        rep = r.json()
        assert rep["document_meta"]["domain"] == "example.ru"
        assert isinstance(rep["scoring"]["overall_score"], int)
        titles = [v["title"] for v in rep["violations"]]
        assert any("Политика обработки ПДн не найдена" in t for t in titles), titles

        # PDF для free → 402
        r = await client.get(f"/api/reports/{report_id}/pdf", headers=auth)
        assert r.status_code == 402, r.status_code

        # Чужой отчёт → 404
        other_email = f"v{uuid.uuid4().hex[:10]}@example.com"
        r2 = await client.post("/api/auth/register",
                               json={"email": other_email, "password": "secretpass1"})
        other = {"Authorization": f"Bearer {r2.json()['token']}"}
        r = await client.get(f"/api/reports/{report_id}", headers=other)
        assert r.status_code == 404

    # Корректно закрываем движок до закрытия loop'а — иначе asyncpg на Windows ругается.
    from app.db import engine as _engine
    await _engine.dispose()


def test_full_flow():
    import asyncio
    _run_migrations()
    asyncio.run(_run_flow())
    print("E2E ALL OK")


if __name__ == "__main__":
    test_full_flow()
