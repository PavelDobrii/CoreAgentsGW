from __future__ import annotations

import asyncio
import os
import pathlib

import pytest
from fastapi.testclient import TestClient

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


class _ResponseWrapper:
    def __init__(self, response):
        self._response = response
        self.status_code = response.status_code
        self.headers = response.headers

    def json(self):
        return self._response.json()

    @property
    def text(self) -> str:
        return self._response.text


class _AsyncTestClient:
    def __init__(self, client: TestClient):
        self._client = client

    async def request(self, method: str, url: str, **kwargs):
        response = self._client.request(method, url, **kwargs)
        return _ResponseWrapper(response)

    async def get(self, url: str, **kwargs):
        return await self.request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs):
        return await self.request("POST", url, **kwargs)

    async def put(self, url: str, **kwargs):
        return await self.request("PUT", url, **kwargs)


@pytest.fixture()
async def async_client():
    with TestClient(app) as client:
        yield _AsyncTestClient(client)
