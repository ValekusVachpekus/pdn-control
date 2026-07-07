# AGENTS.md — руководство для агентов и контрибьюторов

Файл описывает, как работать в репозитории **ПДн Контроль** автоматизированным агентам
(LLM-ассистентам) и людям-контрибьюторам: структура, команды setup/verify, ожидания по
ревью, ограничения безопасности и ссылки на поддерживаемую документацию. Правила
рабочего процесса — в [`CONTRIBUTING.md`](CONTRIBUTING.md); проектные соглашения и
контракты данных — в [`CLAUDE.md`](CLAUDE.md).

## Что это за проект

Веб-сервис предварительного **технического** аудита сайтов на типовые риски нарушения
**152-ФЗ**. Сервис не даёт юридической гарантии — это инструмент снижения рисков.
Pipeline: `URL → парсер (факты JSON) → rule-engine + LLM → единый JSON → фронтенд и PDF-отчёт`.

## Структура репозитория (монорепо)

| Каталог | Назначение | Стек |
|---|---|---|
| [`frontend/`](frontend/) | SPA: ввод URL, дашборд отчёта, история | Vite + React, nginx |
| [`backend/`](backend/) | API + rule-engine + LLM-анализ + оркестрация | FastAPI, Celery, Postgres, Redis |
| [`crowler/`](crowler/) | Парсер/crawler: собирает факты со страниц | Python, Playwright, FastAPI (порт 8010) |
| [`PDFreport/`](PDFreport/) | Генерация PDF из единого JSON | FastAPI + Typst, uv (порт 8020) |
| [`docs/`](docs/) | Поддерживаемая документация (архитектура, качество, UAT, roadmap) |
| [`reports/`](reports/) | Понедельные отчёты по ассайнментам |

Контракты данных (не ломать без синхронного обновления обоих концов):
- **Контракт №1** — парсер → бэкенд: [`crowler/CONTRACT.md`](crowler/CONTRACT.md).
- **Контракт №2** — единый JSON бэкенд → фронтенд и PDF: эталон `PDFreport/example.json`,
  его копия `frontend/app/example-report.json` (при правке — синхронизировать обе).

## Setup и запуск

Полный стек (рекомендуется):

```bash
cd backend && docker compose up        # поднимает backend + crowler + PDFreport + Postgres + Redis
```

> Важно: Docker-стек читает секреты из **`.env.secret`** (не `.env`). Обязателен ключ LLM
> (Qwen) — без него анализ не работает. Подробности и подводные камни — во внутренней
> заметке команды по запуску бэка.

Отдельные подсервисы (для локальной разработки):

```bash
cd frontend && npm install && npm run dev            # http://localhost:8000
cd crowler  && pip install -r requirements.txt && playwright install chromium
cd PDFreport && uv sync && uv run uvicorn service:app --port 8020
```

## Проверки перед PR (verify)

Эти же проверки — гейты CI ([`.github/workflows/ci.yml`](.github/workflows/ci.yml)); PR не мёржится, пока они красные.

```bash
# Lint / format (Python)
ruff check backend/app crowler/pdn_parser PDFreport
ruff format --check backend/app crowler/pdn_parser PDFreport

# Тесты + покрытие критических модулей (гейт ≥30%)
cd backend  && pytest -q          # unit + integration (без e2e); e2e — tests/test_e2e.py
cd crowler  && pytest -q
cd PDFreport && pytest tests/ -q   # нужен Typst
cd frontend && npm test            # Vitest; сборка — npm run build

# Безопасность
bandit -r backend/app crowler/pdn_parser PDFreport --severity-level medium   # обязательный гейт
pip-audit                                                                     # advisory

# Ссылки в Markdown
lychee --config lychee.toml './**/*.md'
```

## Ожидания по ревью и мерджу

- Все изменения — через Pull Request, прямые пуши в `main` запрещены.
- Ветка на каждое изменение: `<номер-issue>-краткое-описание`; PR линкуется `Closes #<номер>`.
- Нужен апрув **минимум одного другого** участника; **implementer ≠ reviewer**.
- Перед мерджем — проверить критерии приёмки из issue и обновить `CHANGELOG.md`
  (секция `[Unreleased]`) для видимых пользователю изменений.
- Тип мерджа — merge commit. Историю не переписывать (кроме удаления случайных секретов).

## Ограничения безопасности (для агентов — обязательно)

- **Не коммитить секреты**: `.env`, `.env.secret`, ключи LLM, OAuth client_secret, ПДн,
  реальные учётные данные. Использовать `.env.example`. Секреты заказчика (production
  OAuth/DNS) — только в приватном канале, не в репозиторий.
- **Анти-SSRF**: краулер ходит по URL, заданным пользователем. Не ослаблять guard
  `crowler/pdn_parser/ssrf.py` (QR-01/QRT-01) — блокирует private/loopback/metadata-адреса.
- **Серверный гейтинг платного отчёта** — источник правды сервер; фронтовый флаг `paid`
  и блюр — только UX, доверять им нельзя.
- **Согласие на ПДн** (152-ФЗ ст. 9) фиксируется на сервере (timestamp + версия политики).
- Не отключать и не обходить CI-гейты; квалити-требования расширять, а не ослаблять.

## Поддерживаемая документация (держать актуальной)

- [`docs/customer-handover.md`](docs/customer-handover.md) — состояние передачи заказчику.
- [`docs/architecture/`](docs/architecture/) — static/dynamic/deployment views + ADR.
- [`docs/quality-requirements.md`](docs/quality-requirements.md) / [`docs/quality-requirement-tests.md`](docs/quality-requirement-tests.md) — QR и QRT.
- [`docs/testing.md`](docs/testing.md), [`docs/definition-of-done.md`](docs/definition-of-done.md), [`docs/user-acceptance-tests.md`](docs/user-acceptance-tests.md).
- [`docs/development-process.md`](docs/development-process.md), [`docs/roadmap.md`](docs/roadmap.md).
- Hosted-сайт: https://valekusvachpekus.github.io/pdn-control/

При изменении рабочего процесса, команд setup/verify, ограничений безопасности, шагов
деплоя или лимитов — обновлять этот файл, [`CONTRIBUTING.md`](CONTRIBUTING.md) и
[`docs/customer-handover.md`](docs/customer-handover.md) в том же PR.
