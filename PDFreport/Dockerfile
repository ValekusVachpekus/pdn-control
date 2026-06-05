# syntax=docker/dockerfile:1

# ---- стадия 1: статический бинарь typst -------------------------------------
FROM debian:bookworm-slim AS typst
ARG TYPST_VERSION=0.14.2
ARG TARGETARCH
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl xz-utils ca-certificates \
 && rm -rf /var/lib/apt/lists/*
RUN set -eux; \
    case "${TARGETARCH:-amd64}" in \
      amd64) arch=x86_64 ;; \
      arm64) arch=aarch64 ;; \
      *) echo "unsupported arch: ${TARGETARCH}" >&2; exit 1 ;; \
    esac; \
    url="https://github.com/typst/typst/releases/download/v${TYPST_VERSION}/typst-${arch}-unknown-linux-musl.tar.xz"; \
    curl -fsSL "$url" -o /tmp/typst.tar.xz; \
    tar -xJf /tmp/typst.tar.xz -C /tmp; \
    mv "/tmp/typst-${arch}-unknown-linux-musl/typst" /usr/local/bin/typst; \
    typst --version

# ---- стадия 2: приложение ---------------------------------------------------
FROM python:3.12-slim

# uv (менеджер зависимостей) и typst — из готовых образов/стадий
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY --from=typst /usr/local/bin/typst /usr/local/bin/typst

# шрифты с кириллицей — иначе Typst не отрисует русский текст
RUN apt-get update \
 && apt-get install -y --no-install-recommends fonts-liberation fonts-dejavu-core \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# зависимости — отдельным слоем, чтобы кэшировались при правках кода
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# исходники сервиса и шаблон
COPY . .

ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health').status==200 else 1)"

CMD ["uvicorn", "service:app", "--host", "0.0.0.0", "--port", "8000"]
