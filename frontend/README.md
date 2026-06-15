# ПДн Контроль — Frontend

React 18 SPA на Vite. JSX компилируется при сборке — никакого Babel в браузере.

## Разработка

```bash
npm install
npm run dev        # http://localhost:8000
npm test           # Vitest + React Testing Library (jsdom)
```

## Тестирование

Тесты на **Vitest + React Testing Library** (`jsdom`), конфиг — в `vite.config.js`
(`test:`), общий setup — `test/setup.js` (матчеры jest-dom, полифилл `requestAnimationFrame`).

- `test/mapReport.test.js` — юнит-тесты адаптера `mapReport`: эталонная фикстура
  `example-report.json` + крайние случаи (пустой объект, нет `total_fine_rub`,
  пустые `violations`, tri-state локализации).
- `test/smoke.test.jsx` — smoke-рендеры `Landing` и `Report` (mock-данные,
  режимы «Владелец»/«Специалист», заглушка `scanFailed`): проверяют, что
  компоненты монтируются без падений.

```bash
npm test                       # один прогон (CI-режим, vitest run)
npx vitest                     # watch-режим при разработке
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

| Метод | Путь | Тело → ответ | Назначение |
|---|---|---|---|
| `POST` | `/api/scans` | `{ url }` → `{ report_id }` | запустить проверку |
| `GET`  | `/api/reports/:id` | → JSON Контракта №2 (+ флаг оплаты) | единый отчёт |
| `GET`  | `/api/reports/:id/pdf` | → `application/pdf` | прокси к PDF-микросервису (только оплаченный) |
| `POST` | `/api/auth/login` | `{ email, password }` → `{ token, user }` | вход |
| `POST` | `/api/auth/register` | `{ email, password, consent }` → `{ token, user }` | регистрация (consent — согласие на ПДн, ст. 9) |
| `*`    | `/api/auth/oauth/:provider` | redirect-flow (+`consent` при регистрации) → сессия + `user` | вход через Яндекс/ВК |
| `GET`  | `/api/billing/plans` | → `Plan[]` | каталог продуктов (витрина) |
| `POST` | `/api/billing/checkout` | `{ plan }` → `{ checkout_url }` | сессия разовой оплаты (CloudPayments) |

`user` = `{ email, provider? }`. `Plan` = `{ id, name, price, highlight, features[] }`,
ровно два продукта: `free` (0 ₽) и `paid` (разовая цена) — **подписок нет**.

> Ещё моки (не часть отчёта, заменить при интеграции): `SCAN_STEPS` — анимация
> лога сканирования (в проде — стрим прогресса), `HISTORY` — история проверок
> (в проде — `GET /api/history`). Оба живут в `app/data.jsx`.

## Аутентификация, оплата и безопасность

Вход (`Auth.jsx`) и оплата (`Pricing.jsx`) — **готовые UI-шаблоны**; вся сеть идёт через
`api.js` (`login`, `register`, `loginWithProvider`, `fetchPlans`, `createCheckout`).
Модель — **разовая оплата** (без подписок): бесплатный отчёт = тизер, платный = разблокировка
одного отчёта. Хардкода нет: каталог продуктов из `fetchPlans()` (MOCK → дефолт, прод → бэкенд).

**Гейтинг (блюр) отчёта** — во фронте: на бесплатном тарифе премиум-блоки `Report.jsx`
заблюрены под оверлеем, видны лишь скоринг/счётчики/заключение. Флаг `paid` — состояние
`App.jsx`, ставится по успеху checkout, сбрасывается на каждой новой проверке.

**Что нужно довести при интеграции бэкенда (сейчас — заглушки/только UX):**
- **Статус оплаты с сервера.** `paid` сейчас живёт только во фронте. В проде разблокировку
  обязан подтверждать бэкенд: флаг в ответе `/api/reports/:id` (оплачен ли отчёт) либо
  отдельная проверка доступа. После возврата из CloudPayments фронт перезапрашивает отчёт.
- **OAuth Яндекс/ВК.** `loginWithProvider` — заглушка (в MOCK возвращает фейк-`user`).
  Реальный вход — redirect-flow: фронт ведёт на `/api/auth/oauth/:provider`, бэкенд
  обрабатывает callback провайдера, ставит сессию и возвращает `user`. Не POST с готовым `user`.
- **Серверный гейтинг (фронт-проверки обходятся):** `/api/billing/checkout` — 401 без
  сессии; `/api/reports/:id/pdf` и премиум-поля отдавать только для оплаченного отчёта.
- `/api/scans` — повторно валидировать URL и резать SSRF (не сканить `localhost`/
  внутренние IP); на фронте уже стоит `isValidDomain` как defense-in-depth.
- Токен/сессия — в `httpOnly`-cookie (фронт не хранит JWT в `localStorage`).

**Известные ограничения демо (закрываются бэкендом):** оплата имитируется и `paid`
сбрасывается при перезагрузке; OAuth — мок; нет выхода из аккаунта — появится с реальным auth.

## Соответствие 152-ФЗ самого сайта

Сайт сам собирает ПДн (e-mail при регистрации), поэтому закрывает типовые требования —
те же, что ловит наш сканер:

- **Cookie-баннер** (`CookieBanner.jsx`) — рендерится глобально в `App.jsx`, кнопки
  «Принять» / **«Отклонить»** (кнопка отказа обязательна — сканер штрафует за её отсутствие).
  Выбор хранится в `localStorage` (`pdn_cookie_consent`); хелперы `getCookieConsent` /
  `setCookieConsent` / `resetCookieConsent`. **В dev (`import.meta.env.DEV`) баннер
  показывается при каждой перезагрузке** для тестирования; в проде — один раз.
- **Согласие на обработку ПДн** (`Auth.jsx`) — чекбокс при регистрации, **снят по
  умолчанию** (ст. 9), без него регистрация и OAuth заблокированы; ссылается на политику.
  Флаг `consent` уходит в `register()` / `loginWithProvider()` — **бэкенд обязан
  зафиксировать факт согласия** (timestamp + версия политики), чтобы суметь его доказать.
  Фронтовая галочка — лишь UX; источник истины — запись на сервере (нет consent → 4xx).
- **Политика обработки ПДн** (`Policy.jsx`) — отдельный экран (`screen='policy'` в
  `App.jsx`), доступен из баннера, галочки регистрации и футера лендинга. Текст —
  **заглушка** между маркерами `POLICY-TEXT-BEGIN/END`, заполняется вручную.

Вне фронта (нужно отдельно): уведомление в Роскомнадзор (ст. 22), локализация БД граждан
РФ в РФ (ст. 18 ч. 5), серверная фиксация согласия и cookie-выбора.

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
    ├── api.js              # ШОВ С БЭКЕНДОМ: scans/reports/auth/billing + isValidDomain (+ MOCK)
    ├── mapReport.js        # адаптер: JSON Контракта №2 → модель UI
    ├── example-report.json # демо-фикстура единого JSON (копия PDFreport/example.json)
    ├── Landing.jsx         # главная страница с формой ввода URL
    ├── Auth.jsx            # вход/регистрация: e-mail + OAuth + чекбокс согласия на ПДн
    ├── CookieBanner.jsx    # cookie-баннер 152-ФЗ (Принять/Отклонить, localStorage)
    ├── Policy.jsx          # экран политики обработки ПДн (заглушка под текст)
    ├── Pricing.jsx         # разовая оплата полного отчёта (шаблон, CloudPayments)
    ├── Scanning.jsx        # экран прогресса проверки (анимация SCAN_STEPS)
    ├── Report.jsx          # страница отчёта
    ├── ReportAppendix.jsx  # техническое приложение
    ├── History.jsx         # история проверок
    ├── shared.jsx          # переиспользуемые компоненты (Icon, Badge, ...)
    ├── data.jsx            # UI-данные НЕ из отчёта: SCAN_STEPS, HISTORY, RISK_BANDS
    ├── tweaks-panel.jsx    # панель настроек (тема, акцент)
    └── styles.css
```
