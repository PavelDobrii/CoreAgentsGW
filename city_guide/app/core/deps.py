from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from .config import settings

engine = create_async_engine(settings.async_database_url, echo=settings.echo_sql)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)


async def get_db() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session


def override_engine(url: str) -> None:
    global engine, SessionLocal
    engine = create_async_engine(url, echo=settings.echo_sql)
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)
