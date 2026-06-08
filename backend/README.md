# ПДн Контроль — backend API

FastAPI-сервис: регистрация/логин, постановка проверок сайта в очередь,
выдача отчётов по Контракту №2 и проксирование PDF через микросервис PDFreport.

## Архитектура

```
[ frontend ] ──HTTP──> [ api (8000) ] ──Celery/Redis──> [ worker ]
                            │                                 │
                            ├── Postgres (users, scans)       ├── crowler (8010)  — факты
                            └── PDFreport (8020) — PDF        └── rule-engine     — нарушения
```

Один таск Celery = одна полная проверка одного сайта: запрос к парсеру,
прогон rule-engine, сохранение готового JSON Контракта №2 в БД.

## Запуск всего стека

```bash
cd backend
docker compose up --build
```

После запуска:

| Сервис       | URL                          |
|--------------|------------------------------|
| API + Swagger| http://localhost:8000/docs   |
| Crawler      | http://localhost:8010/health |
| PDF Report   | http://localhost:8020/health |
| Postgres     | localhost:5432 (pdn/pdn)     |
| Redis        | localhost:6379               |

Миграции применяются автоматически при старте `api`.

## Локальный запуск без Docker

```bash
cd backend
python -m venv .venv && .venv\Scripts\activate
pip install -e .
copy .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
# в другом терминале:
celery -A app.workers.celery_app worker -l info -Q scans
```

Также должны быть запущены: Postgres, Redis, crowler (8010), pdfreport (8020).

## API

| Метод | Путь                          | Auth | Что делает |
|-------|-------------------------------|------|------------|
| POST  | /api/auth/register            | —    | Регистрация (email+пароль) |
| POST  | /api/auth/login               | —    | Логин, выдаёт JWT |
| POST  | /api/scans                    | ✓    | Поставить сайт в проверку |
| GET   | /api/scans/{id}/status        | ✓    | Статус проверки |
| GET   | /api/reports/{id}             | ✓    | JSON Контракта №2 |
| GET   | /api/reports/{id}/pdf         | ✓ paid | PDF-отчёт (через PDFreport) |
| GET   | /api/billing/plans            | —    | Каталог тарифов |
| POST  | /api/billing/checkout         | ✓    | Заглушка под платёжного провайдера |
| GET   | /api/health                   | —    | liveness |

## Контракты

- **Контракт №1** — JSON от парсера. Описан в `../crowler/CONTRACT.md`.
- **Контракт №2** — JSON отчёта (бэк → фронт / бэк → PDFreport). Модели —
  в `../PDFreport/models.py`, пример — в `../frontend/app/example-report.json`.

`app/services/rule_engine.py` — единственное место, где Контракт №1
превращается в Контракт №2.

## SQL-инъекции

ORM SQLAlchemy всегда параметризует запросы (`select(User).where(User.email == x)` —
безопасно). Никаких `text("SELECT ... " + var)` в коде нет. Дополнительно входные
URL/email валидируются через Pydantic.
