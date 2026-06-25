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
COPY scripts ./scripts

# Offline GeoIP-база (MaxMind GeoLite2) для детерминированной страны хостинга.
# Бандлим в образ при сборке, если передан license key:
#   docker build --build-arg MAXMIND_LICENSE_KEY=xxxxx ...
# Без ключа сборка не падает — meta.server_country будет null (страну не
# выдумываем). Лицензия/атрибуция MaxMind — в pdn_parser/data/README.md.
ARG MAXMIND_LICENSE_KEY=""
RUN if [ -n "$MAXMIND_LICENSE_KEY" ]; then \
        python scripts/download_geoip.py --out pdn_parser/data ; \
    else \
        echo "MAXMIND_LICENSE_KEY не задан — GeoIP-база не бандлится; server_country=null"; \
    fi

EXPOSE 8010

# Запускаем под непривилегированным пользователем, который есть в базовом образе.
USER pwuser

CMD ["uvicorn", "pdn_parser.api:app", "--host", "0.0.0.0", "--port", "8010"]
