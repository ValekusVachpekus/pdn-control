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

## Подключение бэкенда

Раскомментировать блок `location /api/` в `nginx.conf` и указать адрес сервиса.
В `docker-compose` бэкенд должен быть доступен как `backend:8001`.

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
    ├── App.jsx             # оркестратор, роутинг
    ├── Landing.jsx         # главная страница с формой ввода URL
    ├── Scanning.jsx        # экран прогресса проверки
    ├── Report.jsx          # страница отчёта
    ├── ReportAppendix.jsx  # техническое приложение
    ├── History.jsx         # история проверок
    ├── shared.jsx          # переиспользуемые компоненты (Icon, Badge, ...)
    ├── data.jsx            # моковые данные
    ├── tweaks-panel.jsx    # панель настроек (тема, акцент)
    └── styles.css
```
