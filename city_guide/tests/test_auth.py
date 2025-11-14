from __future__ import annotations


def test_register_login_and_refresh(client):
    register_payload = {
        "email": "auth.user@example.com",
        "password": "Password123!",
        "firstName": "Auth",
        "lastName": "User",
    }
    register_response = client.post("/v1/register", json=register_payload)
    assert register_response.status_code == 201
    register_data = register_response.json()
    assert register_data["user"]["email"] == register_payload["email"].lower()
    assert "access_token" in register_data
    assert "refresh_token" in register_data

    login_payload = {"email": register_payload["email"], "password": register_payload["password"]}
    login_response = client.post("/v1/login", json=login_payload)
    assert login_response.status_code == 200
    login_data = login_response.json()
    assert login_data["user"]["email"] == register_payload["email"].lower()

    refresh_response = client.post(
        "/v1/refresh", json={"refreshToken": register_data["refresh_token"]}
    )
    assert refresh_response.status_code == 200
    refreshed = refresh_response.json()
    assert refreshed["access_token"]
    assert refreshed["refresh_token"]


def test_login_rejects_invalid_credentials(client, registered_user):
    response = client.post(
        "/v1/login", json={"email": registered_user["email"], "password": "wrong"}
    )
    assert response.status_code == 401
