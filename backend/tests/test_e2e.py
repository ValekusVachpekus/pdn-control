"""End-to-end API проверка на реальном Postgres + Redis.

Перед запуском подняты контейнеры:
    docker run -d --name pdn-pg-test    -e POSTGRES_USER=pdn -e POSTGRES_PASSWORD=pdn \\
        -e POSTGRES_DB=pdn -p 55432:5432 postgres:16-alpine
    docker run -d --name pdn-redis-test -p 56379:6379 redis:7-alpine

Что покрываем:
  - регистрация с consent=true (и отказ при consent=false);
  - логин;
  - постановка проверки и работа Celery-таска (eager, crawler замокан);
  - free-режим: GET /api/reports/{id} возвращает усечённый JSON (без деталей);
  - PDF 402 для free;
  - чужой отчёт = 404;
  - валидация URL отсекает мусор/инъекции;
  - POST /api/billing/checkout помечает отчёт оплаченным (dev-stub);
  - paid-режим: полный JSON + PDF доступен (PDF-сервис замокан);
  - OAuth-эндпоинт пока 501.
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
os.environ["LLM_API_KEY"] = ""  # LLM выключен — не дёргаем внешний API из теста

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
        assert (await client.get("/api/health")).status_code == 200

        # Register без consent → 400
        bad_email = f"u{uuid.uuid4().hex[:10]}@example.com"
        r = await client.post("/api/auth/register",
                              json={"email": bad_email, "password": "secretpass1", "consent": False})
        assert r.status_code == 400, r.text

        # Register с consent=true → 201
        email = f"u{uuid.uuid4().hex[:10]}@example.com"
        r = await client.post("/api/auth/register",
                              json={"email": email, "password": "secretpass1", "consent": True})
        assert r.status_code == 201, r.text
        token = r.json()["token"]
        auth = {"Authorization": f"Bearer {token}"}
        # В UserOut больше нет plan — есть oauth_provider=None
        assert "plan" not in r.json()["user"]
        assert r.json()["user"]["oauth_provider"] is None

        # Дубль → 409
        r = await client.post("/api/auth/register",
                              json={"email": email, "password": "secretpass1", "consent": True})
        assert r.status_code == 409, r.text

        # Логин
        r = await client.post("/api/auth/login",
                              json={"email": email, "password": "secretpass1"})
        assert r.status_code == 200 and r.json()["token"]

        # Неверный пароль → 401
        r = await client.post("/api/auth/login",
                              json={"email": email, "password": "wrongpass"})
        assert r.status_code == 401

        # OAuth — заглушка (501 на yandex/vk, 404 на остальное)
        r = await client.post("/api/auth/oauth/yandex", json={"consent": True})
        assert r.status_code == 501, r.text
        r = await client.post("/api/auth/oauth/google", json={"consent": True})
        assert r.status_code == 404, r.text

        # Plans
        plans = (await client.get("/api/billing/plans")).json()
        assert {p["id"] for p in plans} == {"free", "paid"}, plans
        paid_plan = next(p for p in plans if p["id"] == "paid")
        assert paid_plan["price"] == 990

        # Валидация URL
        r = await client.post("/api/scans",
                              json={"url": "example.ru'; DROP TABLE users--"}, headers=auth)
        assert r.status_code == 422
        r = await client.post("/api/scans", json={"url": "http://localhost"}, headers=auth)
        assert r.status_code == 422

        # Сабмит проверки (парсер замокан)
        with patch("app.workers.tasks.scan_site_sync", side_effect=_fake_scan_site_sync):
            r = await client.post("/api/scans", json={"url": "example.ru"}, headers=auth)
        assert r.status_code == 201, r.text
        report_id = r.json()["report_id"]

        # Статус — done
        r = await client.get(f"/api/scans/{report_id}/status", headers=auth)
        assert r.status_code == 200 and r.json()["status"] == "done"

        # Free-отчёт: видим scoring/summary, но детали скрыты
        r = await client.get(f"/api/reports/{report_id}", headers=auth)
        assert r.status_code == 200, r.text
        rep = r.json()
        assert rep["_paid"] is False
        assert isinstance(rep["scoring"]["overall_score"], int)
        assert rep["executive_summary"]["total_fine_rub"]  # сумма штрафа видна
        # ключевая проверка: нарушения обезличены до id+severity (Issue #54),
        # ни заголовка/статьи/роли, ни деталей — иначе DevTools раскроет суть
        for v in rep["violations"]:
            assert set(v.keys()) <= {"id", "severity"}, v
            assert "title" not in v and "article_152fz" not in v, v
            assert "target_role" not in v, v
            assert "description" not in v and "evidence" not in v and "fine_rub" not in v, v
        # passed_checks — без detail (детали проверок премиум)
        for p in rep["executive_summary"]["passed_checks"]:
            assert "detail" not in p, p
        assert rep["infrastructure_and_geo"]["server_country_ru"] is None
        assert rep["technical_appendix"]["documents_found"] == []

        # PDF на free → 402
        r = await client.get(f"/api/reports/{report_id}/pdf", headers=auth)
        assert r.status_code == 402

        # Чужой отчёт → 404
        other_email = f"v{uuid.uuid4().hex[:10]}@example.com"
        r2 = await client.post("/api/auth/register",
                               json={"email": other_email, "password": "secretpass1", "consent": True})
        other = {"Authorization": f"Bearer {r2.json()['token']}"}
        r = await client.get(f"/api/reports/{report_id}", headers=other)
        assert r.status_code == 404

        # Checkout чужого отчёта → 404
        r = await client.post("/api/billing/checkout",
                              json={"plan": "paid", "report_id": report_id}, headers=other)
        assert r.status_code == 404

        # Checkout своего → 200 + paid=True
        r = await client.post("/api/billing/checkout",
                              json={"plan": "paid", "report_id": report_id}, headers=auth)
        assert r.status_code == 200, r.text
        assert r.json()["paid"] is True

        # После оплаты — полный отчёт
        r = await client.get(f"/api/reports/{report_id}", headers=auth)
        assert r.status_code == 200
        rep = r.json()
        assert rep["_paid"] is True
        assert rep["violations"][0].get("description")
        assert rep["violations"][0].get("evidence") is not None
        assert "ai_analysis" in rep["technical_appendix"]

        # PDF: бьём в pdfreport — мокаем render_pdf
        with patch("app.routers.reports.render_pdf", return_value=b"%PDF-1.4 fake"):
            r = await client.get(f"/api/reports/{report_id}/pdf", headers=auth)
        assert r.status_code == 200, r.text
        assert r.headers["content-type"] == "application/pdf"
        assert r.content.startswith(b"%PDF")

    from app.db import engine as _engine
    await _engine.dispose()


def test_full_flow():
    import asyncio
    _run_migrations()
    asyncio.run(_run_flow())
    print("E2E ALL OK")


if __name__ == "__main__":
    test_full_flow()
