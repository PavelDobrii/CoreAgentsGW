from __future__ import annotations

import os
from dataclasses import dataclass


def _bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    value = value.strip().lower()
    return value in {"1", "true", "yes", "y", "on"}


@dataclass(slots=True)
class Settings:
    app_host: str = os.getenv("APP_HOST", "0.0.0.0")
    app_port: int = int(os.getenv("APP_PORT", "8000"))

    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:postgres@localhost:5432/core_agents_gw",
    )
    testing: bool = _bool("CITY_GUIDE_TESTING", False)
    require_postgres: bool = _bool("REQUIRE_POSTGRES", True)

    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "super-secret-key")
    access_token_exp_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    refresh_token_exp_minutes: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", str(60 * 24 * 7)))

    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    gpt_model: str = os.getenv("GPT_MODEL", "gpt-4o-mini")

    use_google_sources: bool = _bool("USE_GOOGLE_SOURCES", False)

    def __post_init__(self) -> None:
        if self.testing:
            return
        if not self.require_postgres:
            return
        if not self.database_url.startswith(("postgresql+", "postgresql://", "postgres://")):
            raise RuntimeError("City Guide API requires PostgreSQL in non-testing environments")

    @property
    def sync_database_url(self) -> str:
        url = self.database_url
        if url.startswith("postgresql+asyncpg://"):
            return url.replace("postgresql+asyncpg://", "postgresql://", 1)
        if url.startswith("postgresql+psycopg2://"):
            return url.replace("postgresql+psycopg2://", "postgresql://", 1)
        if url.startswith("postgresql+psycopg://"):
            return url.replace("postgresql+psycopg://", "postgresql://", 1)
        if url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql://", 1)
        if url.startswith("sqlite+aiosqlite://"):
            return url.replace("sqlite+aiosqlite://", "sqlite://", 1)
        return url


settings = Settings()
