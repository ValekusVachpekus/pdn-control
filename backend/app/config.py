"""Конфигурация приложения. Все секреты и адреса — только через env / .env."""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "dev"
    app_host: str = "0.0.0.0"
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

    free_max_pages: int = 5
    paid_max_pages: int = 50

    # LLM-провайдер (OpenAI-совместимый API). По умолчанию DeepSeek;
    # для Qwen достаточно поменять base/model. Если ключ пустой — анализ просто
    # не запускается, и paid-юзер получает отчёт без ai_analysis.
    llm_api_base: str = "https://api.deepseek.com/v1"
    llm_api_key: str = ""
    llm_model: str = "deepseek-v4-flash"
    llm_timeout_sec: int = 60

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
