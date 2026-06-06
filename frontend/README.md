# ПДн Контроль — Frontend

React 18 SPA на Vite. JSX компилируется при сборке — никакого Babel в браузере.

## Разработка

```bash
npm install
npm run dev        # http://localhost:8000
```

## Сборка и запуск через Docker

```bash
docker build -t pdn-frontend .
docker run -p 8000:8000 pdn-frontend
```

Открыть: http://localhost:8000

## Данные и единый JSON

Отчёт **не захардкожен**. Фронт и PDF-микросервис потребляют **один и тот же JSON**
(Контракт №2, описание полей — в `CLAUDE.md`). Поток данных:

```
бэкенд → JSON Контракта №2 → mapReport.js → модель UI → компоненты
                 (тот же JSON также уходит в PDF-микросервис)
```

- `app/api.js` — **единственный шов с бэкендом**. Весь сетевой доступ здесь.
- `app/mapReport.js` — адаптер: JSON Контракта №2 → плоская модель UI
  (snake_case→camelCase, `dateHuman`, флаг страны, `articleShort`, рус. роли, статусы).
- `app/example-report.json` — демо-фикстура единого JSON (копия `PDFreport/example.json`;
  при правке контракта синхронизировать обе).

## Подключение бэкенда

Сейчас работает в режиме **MOCK**: отчёт берётся из `example-report.json`. Чтобы
включить реальные запросы, правок в компонентах не нужно — только env и nginx:

```bash
# .env / переменные сборки
VITE_USE_MOCK=false        # включить реальные fetch (по умолчанию true)
VITE_API_BASE=             # база API; пусто = тот же origin через nginx-прокси /api/
```

Затем раскомментировать блок `location /api/` в `nginx.conf` (в `docker-compose`
бэкенд должен быть доступен как `backend:8001`).

Эндпоинты, которые ожидает `api.js` (предполагаемый контракт, согласовать с бэком):

| Метод | Путь | Назначение |
|---|---|---|
| `POST` | `/api/scans` | `{ url }` → `{ report_id }` — запустить проверку |
| `GET`  | `/api/reports/:id` | → JSON Контракта №2 (единый отчёт) |
| `GET`  | `/api/reports/:id/pdf` | → `application/pdf` (прокси к PDF-микросервису) |

> Ещё моки (не часть отчёта, заменить при интеграции): `SCAN_STEPS` — анимация
> лога сканирования (в проде — стрим прогресса), `HISTORY` — история проверок
> (в проде — `GET /api/history`). Оба живут в `app/data.jsx`.

## Структура

```
frontend/
├── index.html              # точка входа Vite
├── main.jsx                # монтирование React
├── vite.config.js
├── package.json
├── nginx.conf
├── Dockerfile              # multi-stage: node (build) → nginx (serve)
└── app/
    ├── App.jsx             # оркестратор, роутинг, загрузка отчёта через api.js
    ├── api.js              # ШОВ С БЭКЕНДОМ: startScan/fetchReport/reportPdfUrl (+ MOCK)
    ├── mapReport.js        # адаптер: JSON Контракта №2 → модель UI
    ├── example-report.json # демо-фикстура единого JSON (копия PDFreport/example.json)
    ├── Landing.jsx         # главная страница с формой ввода URL
    ├── Scanning.jsx        # экран прогресса проверки (анимация SCAN_STEPS)
    ├── Report.jsx          # страница отчёта
    ├── ReportAppendix.jsx  # техническое приложение
    ├── History.jsx         # история проверок
    ├── shared.jsx          # переиспользуемые компоненты (Icon, Badge, ...)
    ├── data.jsx            # UI-данные НЕ из отчёта: SCAN_STEPS, HISTORY, RISK_BANDS
    ├── tweaks-panel.jsx    # панель настроек (тема, акцент)
    └── styles.css
```
