from __future__ import annotations

import uuid

from city_guide.app.db.repo import RouteDraftRepository


def _sample_trip_payload() -> dict:
    return {
        "title": "Weekend in Vilnius",
        "description": "Explore the old town",
        "localityId": "vilnius",
        "start": {
            "id": "start-1",
            "name": "Cathedral Square",
            "address": "Šventaragio g. 1",
            "location": {"lat": 54.685, "lng": 25.287},
        },
        "end": {
            "id": "end-1",
            "name": "Town Hall",
            "address": "Rotušės a. 1",
            "location": {"lat": 54.678, "lng": 25.286},
        },
        "routeOptions": {
            "interests": ["history"],
            "duration": "210",
            "timeOfDay": "Morning",
        },
    }


def test_create_trip_returns_trip_response(client, registered_user):
    payload = _sample_trip_payload()
    response = client.post("/v1/routes", json=payload, headers=registered_user["headers"])
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["title"]
    assert data["status"] == "created"
    assert data["localityId"] == payload["localityId"]
    assert data["startWaypoint"]["name"] == payload["start"]["name"]


def test_list_and_get_trip(client, registered_user):
    payload = _sample_trip_payload()
    created = client.post("/v1/routes", json=payload, headers=registered_user["headers"])
    trip_id = created.json()["id"]

    list_response = client.get("/v1/routes", headers=registered_user["headers"])
    assert list_response.status_code == 200
    items = list_response.json()
    assert len(items) == 1
    assert items[0]["id"] == trip_id

    detail_response = client.get(
        f"/v1/routes/{trip_id}", headers=registered_user["headers"]
    )
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == trip_id


class _StubGPTClient:
    def select_poi(self, user_ctx, candidates, k):
        return [c["poi_id"] for c in candidates[:k]]

    def order_route(self, user_ctx, nodes, matrix):
        return [node["poi_id"] for node in nodes]


def _mock_generation_dependencies(monkeypatch, payload):
    def fake_fetch_places(**kwargs):
        base_lat = payload["start"]["location"]["lat"]
        base_lng = payload["start"]["location"]["lng"]
        return [
            {
                "poi_id": f"place-{idx}",
                "name": f"Point {idx}",
                "lat": base_lat + idx * 0.001,
                "lng": base_lng + idx * 0.001,
                "category": "museum",
                "rating": 4.5,
                "open_now": True,
            }
            for idx in range(3)
        ]

    def fake_distance_matrix(points, mode):
        size = len(points)
        return [[0 for _ in range(size)] for _ in range(size)]

    monkeypatch.setattr("city_guide.app.services.google_poi.fetch_places", fake_fetch_places)
    monkeypatch.setattr("city_guide.app.services.google_directions.distance_matrix", fake_distance_matrix)
    monkeypatch.setattr("city_guide.app.api.v1.routes.get_gpt_client", lambda: _StubGPTClient())


def test_generate_trip_updates_draft(monkeypatch, client, registered_user):
    payload = _sample_trip_payload()
    created = client.post("/v1/routes", json=payload, headers=registered_user["headers"])
    trip_id = created.json()["id"]

    _mock_generation_dependencies(monkeypatch, payload)

    generate_payload = {"waypoints": [], "places": []}
    response = client.post(
        f"/v1/routes/{trip_id}/generate", json=generate_payload, headers=registered_user["headers"]
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Generation started"

    detail_response = client.get(
        f"/v1/routes/{trip_id}", headers=registered_user["headers"]
    )
    data = detail_response.json()
    assert data["status"] == "draft"
    assert data["waypoints"] is not None
    assert len(data["waypoints"]) >= 1

    repo = RouteDraftRepository()
    draft = repo.get_draft(uuid.UUID(trip_id))
    assert draft is not None
    assert len(draft.points) == len(data["waypoints"])
