from __future__ import annotations

import uuid


def test_profile_returns_default_and_allows_updates(client, registered_user):
    headers = registered_user["headers"]
    response = client.get("/v1/profile", headers=headers)
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

    response = client.put("/v1/profile", json=update_payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    for key, value in update_payload.items():
        assert data[key] == value

    response = client.get("/v1/profile", headers=headers)
    assert response.status_code == 200
    assert response.json() == data


def test_profile_context_roundtrip(client):
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

    response = client.post("/v1/profile/context", json=payload)
    assert response.status_code == 201
    assert response.json() == payload

    response = client.get("/v1/profile/context", params={"user_id": str(user_id)})
    assert response.status_code == 200
    assert response.json() == payload
