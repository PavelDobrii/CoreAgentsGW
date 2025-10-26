from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings


def _resolve_env_file() -> str:
    """Return a deterministic path to the environment file.

    PyCharm запускает скрипты из разных рабочих директорий. Чтобы не требовать
    ручного указания переменной ``CITY_GUIDE_ENV`` в каждом конфиге, ищем
    наиболее подходящее расположение ``.env`` относительно корня репозитория.

    Порядок поиска:

    1. Пользовательский путь из ``CITY_GUIDE_ENV`` (если задан).
    2. ``<repo>/.env`` — удобно держать конфиги рядом с run-конфигурациями.
    3. ``<repo>/city_guide/.env`` — историческое местоположение.

    Если файл ещё не создан, возвращаем первый кандидат, чтобы Pydantic мог
    работать с пустым значением и PyCharm предлагал создать файл в ожидаемом
    месте.
    """

    env_override = os.getenv("CITY_GUIDE_ENV")
    if env_override:
        return env_override

    project_root = Path(__file__).resolve().parents[2]
    candidates = [project_root / ".env", project_root / "city_guide" / ".env"]

    for candidate in candidates:
        if candidate.exists():
            return str(candidate)

    return str(candidates[0])


def _parse_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        value = value.strip().lower()
        if value in {"1", "true", "yes", "y", "on"}:
            return True
        if value in {"0", "false", "no", "n", "off"}:
            return False
    return default


class Settings(BaseSettings):
    database_url: str = Field(env="DATABASE_URL")
    echo_sql: bool = Field(default=False, validation_alias="ECHO_SQL")

    openai_api_key: str | None = Field(default=None, env="OPENAI_API_KEY")
    gpt_model: str = Field(default="gpt-4o-mini", env="GPT_MODEL")

    google_maps_api_key: str | None = Field(default=None, env="GOOGLE_MAPS_API_KEY")
    use_google_sources: bool = Field(default=True, env="USE_GOOGLE_SOURCES")
    places_radius_m: int = Field(default=2500, env="PLACES_RADIUS_M")
    places_max_results: int = Field(default=20, env="PLACES_MAX_RESULTS")

    app_host: str = Field(default="0.0.0.0", env="APP_HOST")
    app_port: int = Field(default=8000, env="APP_PORT")

    class Config:
        env_file = _resolve_env_file()
        env_file_encoding = "utf-8"

    @property
    def async_database_url(self) -> str:
        if self.database_url.startswith("postgresql+psycopg2://"):
            url = self.database_url.replace("postgresql+psycopg2://", "postgresql+asyncpg://", 1)
        elif self.database_url.startswith("postgresql+psycopg://"):
            url = self.database_url.replace("postgresql+psycopg://", "postgresql+asyncpg://", 1)
        elif self.database_url.startswith("postgresql+"):
            url = self.database_url
        elif self.database_url.startswith("postgresql://"):
            url = self.database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif self.database_url.startswith("postgres://"):
            url = self.database_url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif self.database_url.startswith("sqlite+aiosqlite://"):
            url = self.database_url
        elif self.database_url.startswith("sqlite://"):
            url = self.database_url.replace("sqlite://", "sqlite+aiosqlite://", 1)
        else:
            raise ValueError("Unsupported database URL")
        return url

    @property
    def sync_database_url(self) -> str:
        if self.database_url.startswith("postgresql+asyncpg://"):
            return self.database_url.replace("postgresql+asyncpg://", "postgresql://", 1)
        if self.database_url.startswith("postgresql+psycopg2://"):
            return self.database_url.replace("postgresql+psycopg2://", "postgresql://", 1)
        if self.database_url.startswith("postgresql+psycopg://"):
            return self.database_url.replace("postgresql+psycopg://", "postgresql://", 1)
        if self.database_url.startswith("postgres://"):
            return self.database_url.replace("postgres://", "postgresql://", 1)
        if self.database_url.startswith("sqlite+aiosqlite://"):
            return self.database_url.replace("sqlite+aiosqlite://", "sqlite://", 1)
        return self.database_url

    def bool_from_env(self, value: Any, default: bool = False) -> bool:
        return _parse_bool(value, default)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
