from __future__ import annotations

import uuid

import pytest


@pytest.mark.asyncio
async def test_profile_returns_default_and_allows_updates(async_client, registered_user):
    headers = registered_user["headers"]
    response = await async_client.get("/v1/profile", headers=headers)
    assert response.status_code == 200
    assert response.json() == registered_user["user"]

    update_payload = {
        "city": "Kaunas",
        "language": "lt",
        "travelStyle": "relaxed",
        "interests": ["food", "art"],
        "gender": "female",
        "age": 32,
        "region": "Kaunas County",
    }

    response = await async_client.put("/v1/profile", json=update_payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    for key, value in update_payload.items():
        assert data[key] == value

    response = await async_client.get("/v1/profile", headers=headers)
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
