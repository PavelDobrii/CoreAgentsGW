from __future__ import annotations

import uuid

import pytest

from city_guide.app.api.v1 import profile as profile_module


@pytest.mark.asyncio
async def test_profile_returns_default_and_allows_updates(async_client):
    response = await async_client.get("/v1/profile")
    assert response.status_code == 200
    assert response.json() == profile_module.DEFAULT_PROFILE_TEMPLATE.model_dump(by_alias=True)

    update_payload = {
        "city": "Kaunas",
        "language": "lt",
        "travelStyle": "relaxed",
        "interests": ["food", "art"],
        "gender": "female",
        "age": 32,
        "region": "Kaunas County",
    }

    response = await async_client.put("/v1/profile", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    for key, value in update_payload.items():
        assert data[key] == value

    response = await async_client.get("/v1/profile")
    assert response.status_code == 200
    assert response.json() == data


@pytest.mark.asyncio
async def test_profile_context_roundtrip(async_client):
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

    response = await async_client.post("/v1/profile/context", json=payload)
    assert response.status_code == 201
    assert response.json() == payload

    response = await async_client.get("/v1/profile/context", params={"user_id": str(user_id)})
    assert response.status_code == 200
    assert response.json() == payload
