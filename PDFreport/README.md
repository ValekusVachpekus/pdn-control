# PDF Report — ПДн Контроль

Микросервис генерации PDF-отчёта из JSON. Рендеринг — через [Typst](https://typst.app).

На вход подаётся JSON по контракту **«бэкенд → PDF Report микросервис» (Контракт №2)**;
на выходе — готовый PDF-отчёт с риск-скорингом, списком нарушений и техническим
приложением.

> Отчёт сознательно содержит дисклеймер: это предварительный технический аудит,
> **не** юридическая гарантия соответствия 152-ФЗ.

## Файлы

| Файл | Назначение |
|------|------------|
| `service.py` | HTTP-сервис (FastAPI): эндпоинты `/health` и `/render`. |
| `renderer.py` | `render_pdf(report: dict) -> bytes` — компиляция PDF через Typst. |
| `models.py` | Pydantic-модели Контракта №2 (валидация входного JSON). |
| `template.typ` | Шаблон отчёта. Читает данные и рендерит PDF. |
| `example.json` | Пример входного JSON (Контракт №2) для превью/тестов. |
| `pyproject.toml` | Зависимости и метаданные проекта (управляется `uv`). |
| `.gitignore` | Игнорирует артефакты (`*.pdf`, `*.png`, `data.json`) и `.venv/`. |

## Требования

- `python` ≥ 3.11 и [`uv`](https://docs.astral.sh/uv/) (управление зависимостями/запуск).
- `typst` ≥ 0.12 (разрабатывалось на 0.14.2) — бинарь в `PATH`.
- Шрифты с кириллицей. Шаблон использует стек `Inter → Liberation Sans → DejaVu Sans`;
  если ни один не установлен, Typst подставит свой дефолтный шрифт (тоже с кириллицей).
  Для фирменного вида установите [Inter](https://rsms.me/inter/).

## Запуск сервиса

```sh
uv sync                                              # установить зависимости
uv run uvicorn service:app --host 0.0.0.0 --port 8000
```

### HTTP API

| Метод | Путь | Описание |
|-------|------|----------|
| `GET`  | `/health` | Живость + доступность typst: `{"status":"ok","typst":true}`. |
| `POST` | `/render` | Тело — JSON по Контракту №2. Ответ — `application/pdf`. |

Коды ответа `/render`: `200` — PDF; `422` — JSON не прошёл валидацию (детали полей
в теле ошибки); `500` — ошибка компиляции шаблона; `503` — `typst` недоступен.

```sh
# сгенерировать отчёт из примера
curl -X POST http://localhost:8000/render \
  -H 'Content-Type: application/json' \
  --data @example.json -o report.pdf
```

Интерактивная схема и форма для запросов — на `/docs` (Swagger UI).

## Превью на примере

```sh
typst compile --input data=example.json template.typ preview.pdf
# или в картинки:
typst compile --input data=example.json --format png template.typ "page-{n}.png"
```

Откуда берутся данные: шаблон читает путь из `sys.inputs.data`
(`--input data=<path>`), а если он не задан — из `data.json` рядом с шаблоном.
Путь к JSON разрешается относительно `template.typ` либо как абсолютный (в пределах
`--root`, см. ниже).

## Как устроен рендеринг

Typst в целях безопасности не читает файлы вне корня проекта (`--root`). Поэтому
`renderer.render_pdf()` на каждый запрос создаёт изолированную рабочую папку, кладёт
туда `data.json` и копию шаблона и компилирует с `--root` на эту папку — это безопасно
и корректно работает при параллельных запросах. Функцию можно использовать и напрямую,
без HTTP:

```python
from renderer import render_pdf

pdf_bytes = render_pdf(report_dict)   # report_dict — данные по Контракту №2
```

## Контракт входного JSON

Полное описание полей — в `CLAUDE.md` проекта (раздел «Контракт №2»). Кратко:

- `document_meta` — метаданные отчёта (`report_id`, `generated_at`, `target_url`,
  `domain`, `organization_name`, `scan_duration_sec`, `pages_scanned`, `scanner_version`).
- `scoring` — `overall_score` (0–100), `risk_level`
  (`CRITICAL|HIGH|MEDIUM|LOW|SAFE`), `risk_label_ru`, `legal_score`, `technical_score`.
- `executive_summary` — `verdict` + `stats`
  (`critical_count`, `warning_count`, `info_count`, `passed_count`).
- `infrastructure_and_geo` — IP/страна/хостинг, `localization_compliant` (bool),
  `localization_note`.
- `violations[]` — `id`, `severity` (`critical|warning|info`), `article_152fz`,
  `title`, `description`, `evidence[]`, `target_role`
  (`developer|lawyer|marketer`), `recommendation`.
- `technical_appendix` — `documents_found[]`, `trackers_summary`
  (`total`/`russian`/`foreign`/`list`), `data_collection_points[]`.

### Устойчивость шаблона

- `null` в полях рендерится как «—».
- Пустой `violations` → блок «Нарушений не выявлено».
- Пустые `documents_found` / `data_collection_points` → текстовая заглушка.
- Неизвестные значения `risk_level` / `severity` / `target_role` не ломают
  компиляцию (есть дефолты).
