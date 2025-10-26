from __future__ import annotations

import uuid

import pytest


@pytest.mark.asyncio
async def test_create_and_get_profile(async_client):
    user_id = uuid.uuid4()
    payload = {
        "user_id": str(user_id),
        "city": "Vilnius",
        "language": "en",
        "travel_style": "relaxed",
        "interests": ["history", "art"],
        "transport_mode": "walking",
        "duration_min": 180,
    }

    response = await async_client.post("/v1/profile", json=payload)
    assert response.status_code == 201
    assert response.json() == payload

    response = await async_client.get("/v1/profile", params={"user_id": str(user_id)})
    assert response.status_code == 200
    assert response.json() == payload
