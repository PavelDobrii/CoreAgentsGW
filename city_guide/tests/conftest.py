from __future__ import annotations

import pytest

from city_guide.app.core import deps
from city_guide.app.http import TestClient
from city_guide.app.main import app


def _create_registered_user(client: TestClient):
    payload = {
        "email": "demo.user@example.com",
        "password": "SuperSecret123",
        "firstName": "Demo",
        "lastName": "User",
        "phoneNumber": "+10000000000",
        "country": "Lithuania",
        "city": "Vilnius",
    }
    response = client.post("/v1/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    return {
        "email": payload["email"],
        "password": payload["password"],
        "headers": {"Authorization": f"Bearer {data['access_token']}"},
        "tokens": data,
        "user": data["user"],
    }


@pytest.fixture(autouse=True)
def reset_state():
    deps.reset_state()
    yield
    deps.reset_state()


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def registered_user(client: TestClient):
    return _create_registered_user(client)
