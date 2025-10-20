from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_health(async_client):
    response = await async_client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
