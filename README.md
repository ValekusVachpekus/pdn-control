# ПДн Контроль

Веб-сервис для предварительного **технического** аудита сайтов малого и среднего
бизнеса на типовые риски нарушения **152-ФЗ** «О персональных данных». MVP.

> ⚠️ Сервис **не даёт юридической гарантии** и не обещает «полное соответствие
> 152-ФЗ за 5 минут». Это инструмент снижения типовых рисков, а не заключение юриста.

## Что делает

- ввод URL → запуск проверки;
- crawler публичных страниц сайта;
- обнаружение форм, cookie, скриптов/трекеров, политик;
- rule-based проверка типовых нарушений + AI-анализ текстов политик и согласий;
- риск-скоринг, список нарушений с приоритетами и рекомендациями, PDF-отчёт;
- история проверок.

## Структура репозитория (монорепо)

| Каталог | Назначение | Стек | README |
|---|---|---|---|
| [`frontend/`](frontend/) | Веб-интерфейс (SPA): ввод URL, дашборд отчёта, история | Vite + React, nginx | [frontend/README.md](frontend/README.md) |
| [`crowler/`](crowler/) | Парсер/crawler: собирает факты со страниц, отдаёт JSON | Python, Playwright, FastAPI | [crowler/README.md](crowler/README.md) |
| [`PDFreport/`](PDFreport/) | Микросервис генерации PDF-отчёта из JSON | FastAPI + Typst, uv | [PDFreport/README.md](PDFreport/README.md) |

Pipeline: `URL → парсер (факты JSON) → rule-engine + LLM → единый JSON → фронтенд и PDF-отчёт`.

## Документация

- [crowler/CONTRACT.md](crowler/CONTRACT.md) — контракт парсер → бэкенд (схема JSON фактов).
- Контракт единого JSON (бэкенд → фронтенд и PDF) — см. `PDFreport/example.json` и
  `frontend/app/example-report.json` (эталонная фикстура).
- [docs/user-stories.md](docs/user-stories.md) — индекс бэклога: пользовательские истории
  (`US-xx`) с ссылками на GitHub Issues (живой источник) и статусом трассируемости.
- [CONTRIBUTING.md](CONTRIBUTING.md) — рабочий процесс: ветки, PR, релизы.
- [CHANGELOG.md](CHANGELOG.md) — история изменений (Keep a Changelog / SemVer).

## Отчёты по неделям

- [reports/week3/README.md](reports/week3/README.md) — индекс сдачи Assignment 3
  (продуктовый бэклог, рефайнмент, оценка в Story Points, спринт).
- [reports/week2/README.md](reports/week2/README.md) — индекс сдачи Assignment 2
  (user stories, прототип, MVP v0, встреча с заказчиком, анализ).
- [reports/week2/mvp-v0-report.md](reports/week2/mvp-v0-report.md) — описание MVP v0,
  деплой, видео-демо и smoke-check сценарий.

## Локальный запуск

Каждый подсервис запускается независимо; полные инструкции — в README соответствующего
каталога. Конфигурация через переменные окружения — см. [`.env.example`](.env.example).

### Frontend

```bash
cd frontend
npm install
npm run dev        # http://localhost:8000
```

### Crowler (парсер)

```bash
cd crowler
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
python -m pdn_parser https://example.com          # JSON-отчёт в stdout
# либо как HTTP-сервис:
docker compose up --build                          # http://localhost:8010
```

### PDF-отчёт

```bash
cd PDFreport
uv sync
uv run uvicorn service:app --host 0.0.0.0 --port 8020
# либо:
docker compose up --build                          # http://localhost:8020
```

## Деплой / runnable-артефакт

Каждый подсервис имеет `Dockerfile` и `docker-compose.yml` для контейнерного запуска
(порты: frontend `8000`, crowler `8010`, PDFreport `8020`). Ссылка на актуальный деплой
и демо публикуются в [Releases](https://github.com/ValekusVachpekus/pdn-control/releases) по мере выхода версий.

## Лицензия

Контент, созданный командой, распространяется по лицензии [MIT](LICENSE). Сторонние
зависимости устанавливаются через менеджеры пакетов и сохраняют свои лицензии.
