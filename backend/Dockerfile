FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DEFAULT_TIMEOUT=300 \
    PIP_RETRIES=10

# Опциональный mirror PyPI (например, mirrors.aliyun.com или nexus компании).
# Передаётся через docker build / docker compose: build.args.PIP_INDEX_URL.
ARG PIP_INDEX_URL=
ENV PIP_INDEX_URL=${PIP_INDEX_URL}

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Пакет приложения (`app`) нужен уже на этапе `pip install .`: pyproject объявляет
# `[tool.setuptools] packages = ["app"]`, поэтому каталог копируем ДО установки,
# иначе сборка wheel падает с `package directory 'app' does not exist`.
COPY pyproject.toml ./
COPY app ./app
RUN pip install --upgrade pip && pip install .

COPY alembic ./alembic
COPY alembic.ini ./
# Тексты законов — нужны llm_analyzer'у на каждый вызов
COPY resources ./resources

# Непривилегированный пользователь: не бежим от root (defense-in-depth).
RUN useradd --create-home --uid 10001 appuser && chown -R appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
