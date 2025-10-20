from __future__ import annotations

import asyncio
import os
import pathlib

import pytest
from httpx import AsyncClient

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test_cityguide.db")
os.environ.setdefault("ECHO_SQL", "false")

from city_guide.app.main import app  # noqa: E402
from city_guide.app.core import deps  # noqa: E402
from city_guide.app.db.models import Base  # noqa: E402

TEST_DB = os.environ["DATABASE_URL"]


@pytest.fixture(scope="session")
def event_loop() -> asyncio.AbstractEventLoop:
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_database() -> None:
    deps.override_engine(TEST_DB)
    async with deps.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with deps.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    db_path = pathlib.Path(TEST_DB.split("///")[-1])
    if db_path.exists():
        db_path.unlink()


@pytest.fixture(autouse=True)
async def clean_database() -> None:
    async with deps.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest.fixture()
async def async_client() -> AsyncClient:
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
