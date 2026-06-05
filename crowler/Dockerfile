# Парсер ПДн Контроль как HTTP-микросервис.
# Базовый образ Playwright уже содержит Chromium и все системные зависимости.
FROM mcr.microsoft.com/playwright/python:v1.49.0-jammy

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    MAX_CONCURRENT_SCANS=2 \
    SCAN_TIMEOUT_SEC=300

WORKDIR /app

# Сначала зависимости — для кэширования слоёв.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && playwright install chromium

# Код пакета (schema.json лежит внутри пакета и копируется вместе с ним).
COPY pdn_parser ./pdn_parser

EXPOSE 8010

# Запускаем под непривилегированным пользователем, который есть в базовом образе.
USER pwuser

CMD ["uvicorn", "pdn_parser.api:app", "--host", "0.0.0.0", "--port", "8010"]
