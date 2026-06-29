"""Конфигурация приложения. Все секреты и адреса — только через env / .env."""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "dev"
    # Слушаем все интерфейсы намеренно: сервис работает в контейнере, наружу его
    # публикует reverse-proxy/оркестратор, а не сам процесс. nosec B104.
    app_host: str = "0.0.0.0"  # noqa: S104  # nosec B104
    app_port: int = 8000

    database_url: str = "postgresql+asyncpg://pdn:pdn@db:5432/pdn"

    redis_url: str = "redis://redis:6379/0"
    celery_broker_url: str = "redis://redis:6379/1"
    celery_result_backend: str = "redis://redis:6379/2"

    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 30  # 30 дней

    crawler_url: str = "http://crowler:8010"
    pdfreport_url: str = "http://pdfreport:8020"

    cors_origins: str = "http://localhost:5173"

    # Сколько страниц парсер обходит за одну проверку. Подписок нет, лимит
    # одинаковый для всех — оплачивается не глубина скана, а доступ к отчёту.
    # 20 — компромисс: успеваем найти политику + cookie + 2-3 формы без
    # риска уйти за SCAN_TIMEOUT_SEC=300 на тяжёлых SPA (spotify, ozon).
    paid_max_pages: int = 20

    # LLM-провайдер (OpenAI-совместимый API). По умолчанию DeepSeek;
    # для Qwen достаточно поменять base/model. Если ключ пустой — анализ просто
    # не запускается, и paid-юзер получает отчёт без ai_analysis.
    # По умолчанию — Alibaba DashScope, модель qwen3.6-plus (1M context).
    # qwen-plus имеет всего 128К контекста, нам не хватает (текст 152-ФЗ + КоАП
    # = ~280К токенов на русском), и DashScope рвёт соединение broken pipe.
    # qwen3.6-plus — оптимум по балансу контекст/цена/качество.
    llm_api_base: str = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
    llm_api_key: str = ""
    llm_model: str = "qwen3.6-plus"
    llm_timeout_sec: int = 60

    # ── E-mail (passwordless OTP) ────────────────────────────────────────────
    # Транзакционная отправка через Resend (HTTP API). Если ключ пуст — DEV-режим:
    # код печатается в лог, письмо не уходит (см. services/email.py). Чтобы
    # включить реальную отправку, достаточно ЗАДАТЬ ДАННЫЕ: resend_api_key +
    # email_from на верифицированный домен — код менять не нужно.
    resend_api_key: str = ""
    email_from: str = "ПДн Контроль <onboarding@resend.dev>"
    email_api_base: str = "https://api.resend.com"

    # OTP-параметры passwordless-входа по коду на e-mail.
    otp_ttl_sec: int = 600              # код живёт 10 минут
    otp_max_attempts: int = 5          # попыток ввода на один код (анти-брутфорс)
    otp_resend_cooldown_sec: int = 60  # не чаще 1 кода/мин на email и на IP

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def email_configured(self) -> bool:
        """Есть ли данные для реальной отправки писем (иначе DEV-режим в лог)."""
        return bool(self.resend_api_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()
