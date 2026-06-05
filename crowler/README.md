# Парсер «ПДн Контроль»

Crawler публичных страниц сайта + детекторы фактов для предварительного
аудита рисков по 152-ФЗ. Парсер **собирает факты**, не делает юридических
выводов и не считает риск-скоринг — это задача rule-engine и LLM, которые
получают результат парсера на вход.

Формат ответа (JSON-конверт `meta + summary + site_identity + policy_documents +
pages`, schema 1.2) полностью описан в [CONTRACT.md](CONTRACT.md); пример —
[json_example.txt](json_example.txt). JSON Schema лежит в
[pdn_parser/schema.json](pdn_parser/schema.json) (путь доступен через
`pdn_parser.schema_path()`).

## Что собирает

Для каждой страницы:

- **Формы** — поля (с видимыми подписями `label` для LLM), базовые категории ПДн
  (email, телефон, ФИО, паспорт, адрес, платёжные данные), загрузка файлов, чекбоксы
  согласия (полный текст, признак «галка по умолчанию», ссылка на политику).
  Чувствительность данных (здоровье, биометрия) парсер не угадывает — это решает LLM
  по подписям и текстам.
- **Cookie** — реально выставленные cookie (свои/сторонние), наличие
  cookie-баннера в DOM (полный текст) и кнопок «принять / отклонить / настройки».
- **Скрипты и трекеры** — метрики (Яндекс.Метрика, GA, GTM, top.mail.ru),
  рекламные пиксели (FB, VK, Google/Yandex Ads), CRM и чат-виджеты
  (JivoSite, Битрикс24, amoCRM, Carrot quest…), капча, карты, платёжки, с флагом
  `cross_border` (передача за рубеж). Источник — теги `<script>` **и** сетевые запросы.
- **Политики** — ссылки на политику/согласие/cookie-политику/оферту, плюс
  **скачанные и очищенные тексты** документов (`policy_documents`) — основной вход для LLM.
- **Передача третьим лицам** — список сторонних доменов, к которым реально
  обращалась страница при загрузке.

По всему сайту дополнительно собираются: агрегированный `summary` с факт-флагами
(есть политика, есть баннер, формы с ПДн без согласия, отслеживание до согласия,
трансграничная передача) и `site_identity` — реквизиты оператора (ИНН/ОГРН/название/
контакты), извлечённые со страниц.

## Установка

```bash
cd crowler
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

## Запуск

```bash
# JSON-отчёт в stdout
python -m pdn_parser https://example.com

# с ограничениями обхода и сохранением в файл
python -m pdn_parser example.ru --max-pages 30 --max-depth 2 -o report.json
```

Опции: `--max-pages`, `--max-depth`, `--ignore-robots`, `--no-headless`,
`--timeout`, `--scan-id`, `--policy-text-to-files`, `-o/--output`, `--indent`.

## Запуск как HTTP-микросервис (Docker)

Парсер можно поднять как сервис — бэкенд шлёт URL, получает JSON-конверт в ответ.

```bash
cd crowler
docker compose up --build        # поднимет сервис на http://localhost:8010
```

Эндпоинты:

| Метод | Путь | Назначение |
|-------|------|------------|
| `POST` | `/scan` | Обойти сайт, вернуть JSON-конверт (schema 1.2). |
| `GET`  | `/health` | Проверка живости + версии. |
| `GET`  | `/schema` | JSON Schema ответа. |
| `GET`  | `/docs` | Авто-документация (Swagger UI). |

Пример запроса:

```bash
curl -X POST http://localhost:8010/scan \
  -H "Content-Type: application/json" \
  -d '{"url": "kazan-clinic.ru", "max_pages": 5, "page_timeout_ms": 30000}'
```

Тело запроса (`/scan`): `url` (обязателен), `max_pages`, `max_depth`,
`respect_robots`, `page_timeout_ms`, `scan_id` (опционально). В ответ — тот же
JSON, что у CLI (`meta + summary + site_identity + policy_documents + pages`).

Переменные окружения сервиса:
- `MAX_CONCURRENT_SCANS` — сколько проверок одновременно (каждая поднимает свой
  браузер; по умолчанию 2);
- `SCAN_TIMEOUT_SEC` — жёсткий лимит на одну проверку (по умолчанию 300 c);
  при превышении сервис вернёт `504`.

> Проверка идёт синхронно и может занимать минуту и больше — бэкенд должен ставить
> щедрый HTTP-таймаут на запрос к `/scan`. Для масштабирования позже стоит вынести
> проверки в очередь задач (паттерн scan_id + поллинг статуса заложен в `meta`).

Без Docker сервис запускается так же:

```bash
uvicorn pdn_parser.api:app --host 0.0.0.0 --port 8010
```

## Как использовать из кода

```python
import asyncio
from pdn_parser import crawl_site

result = asyncio.run(crawl_site("https://example.com", max_pages=10))
for page in result.pages:
    print(page.url, [t.name for t in page.trackers])
```

`crawl_site(...)` возвращает `CrawlResult`; `result.to_dict()` — готовый к
сериализации словарь, который уходит дальше по пайплайну сервиса.

## Структура

```
crowler/
  pdn_parser/
    crawler.py      # обход сайта (robots, sitemap, BFS, лимиты) + сборка envelope
    fetcher.py      # рендеринг страницы Playwright + перехват cookie/запросов
    detectors/      # forms, cookies, scripts, policies
    summary.py      # агрегация фактов по сайту -> SiteSummary
    policy_text.py  # скачивание и очистка текстов политик для LLM
    identity.py     # извлечение реквизитов оператора (ИНН/ОГРН/контакты)
    signatures.py   # сигнатуры трекеров/CRM (+ cross_border) и ключевые слова
    models.py       # структуры данных (dataclasses -> JSON)
    schema.json     # JSON Schema контракта (Draft 2020-12)
    utils.py        # URL/домены, scan_id, время
    cli.py          # точка входа
  CONTRACT.md       # описание JSON-контракта с бэкендом
```

## Границы MVP

- Сигнатуры трекеров и список публичных суффиксов доменов неполные —
  расширяются по мере появления кейсов.
- Детектор cookie-баннера и чекбоксов согласия эвристический (текст + ключевые
  слова), возможны пропуски на нестандартной вёрстке.
- Это предварительный технический аудит, а не гарантия соответствия 152-ФЗ.
