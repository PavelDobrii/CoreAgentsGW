from __future__ import annotations

import uuid

from city_guide.app.core.config import settings
from city_guide.app.db.repo import RouteDraftRepository
from city_guide.app.schemas.poi import BrainstormPOIResponse, BrainstormedPOI


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


_SAMPLE_BRAINSTORMED = [
    BrainstormedPOI(
        title="MO Museum",
        city="Vilnius",
        country="Lithuania",
        category="museum",
        description="Modern art museum",
        priority=0.9,
    ),
    BrainstormedPOI(
        title="Gediminas Tower",
        city="Vilnius",
        country="Lithuania",
        category="viewpoint",
        description="Historic tower",
        priority=0.8,
    ),
]


class _StubGPTClient:
    def __init__(self, brainstorm_items: list[BrainstormedPOI]):
        self._items = brainstorm_items

    async def brainstorm_poi(self, req):  # noqa: D401 - simple stub
        return BrainstormPOIResponse(items=self._items)

    async def select_poi(self, user_ctx, candidates, k):  # noqa: D401 - simple stub
        return [c["poi_id"] for c in candidates[:k]]

    async def order_route(self, user_ctx, nodes, matrix):  # noqa: D401 - simple stub
        return [node["poi_id"] for node in nodes]


def _mock_generation_dependencies(
    monkeypatch,
    brainstorm_items,
    validated_candidates,
    fallback_candidates=None,
):
    monkeypatch.setattr(settings, "use_google_sources", True)
    monkeypatch.setattr(settings, "google_maps_api_key", "fake-test-key")

    monkeypatch.setattr(
        "city_guide.app.api.v1.routes.get_gpt_client",
        lambda: _StubGPTClient(brainstorm_items),
    )

    async def fake_validate_brainstormed_poi(*args, **kwargs):
        return validated_candidates

    monkeypatch.setattr(
        "city_guide.app.services.google_poi.validate_brainstormed_poi",
        fake_validate_brainstormed_poi,
    )

    if fallback_candidates is not None:
        def fake_fetch_places(**kwargs):
            return fallback_candidates

        monkeypatch.setattr(
            "city_guide.app.services.google_poi.fetch_places", fake_fetch_places
        )


def test_generate_trip_updates_draft(monkeypatch, client, registered_user):
    payload = _sample_trip_payload()
    created = client.post("/v1/routes", json=payload, headers=registered_user["headers"])
    trip_id = created.json()["id"]

    validated_candidates = [
        {
            "poi_id": "place-museum",
            "name": "MO Museum",
            "lat": 54.689,
            "lng": 25.279,
            "category": "museum",
            "place_id": "place-museum",
            "source": "google_places",
        },
        {
            "poi_id": "place-tower",
            "name": "Gediminas Tower",
            "lat": 54.686,
            "lng": 25.29,
            "category": "viewpoint",
            "place_id": "place-tower",
            "source": "google_places",
        },
    ]

    _mock_generation_dependencies(monkeypatch, _SAMPLE_BRAINSTORMED, validated_candidates)

    response = client.post(
        f"/v1/routes/{trip_id}/generate", json={"waypoints": [], "places": []}, headers=registered_user["headers"]
    )
    assert response.status_code == 200

    detail_response = client.get(
        f"/v1/routes/{trip_id}", headers=registered_user["headers"]
    )
    data = detail_response.json()
    assert data["status"] == "draft"
    assert len(data["waypoints"]) == len(validated_candidates)

    for waypoint, candidate in zip(data["waypoints"], validated_candidates):
        assert waypoint["lat"] == candidate["lat"]
        assert waypoint["lng"] == candidate["lng"]
        assert waypoint["poi_id"] == candidate["poi_id"]

    repo = RouteDraftRepository()
    draft = repo.get_draft(uuid.UUID(trip_id))
    assert draft is not None
    assert len(draft.points) == len(data["waypoints"])


def test_generate_trip_falls_back_to_legacy_candidates(monkeypatch, client, registered_user):
    payload = _sample_trip_payload()
    created = client.post("/v1/routes", json=payload, headers=registered_user["headers"])
    trip_id = created.json()["id"]

    fallback_candidates = [
        {
            "poi_id": "fallback-1",
            "name": "Legacy Point 1",
            "lat": 54.68,
            "lng": 25.28,
            "category": "sight",
            "source": "fallback",
        },
        {
            "poi_id": "fallback-2",
            "name": "Legacy Point 2",
            "lat": 54.681,
            "lng": 25.281,
            "category": "sight",
            "source": "fallback",
        },
    ]

    _mock_generation_dependencies(
        monkeypatch,
        brainstorm_items=[],
        validated_candidates=[],
        fallback_candidates=fallback_candidates,
    )

    response = client.post(
        f"/v1/routes/{trip_id}/generate", json={"waypoints": [], "places": []}, headers=registered_user["headers"]
    )
    assert response.status_code == 200

    detail_response = client.get(
        f"/v1/routes/{trip_id}", headers=registered_user["headers"]
    )
    data = detail_response.json()
    assert data["status"] == "draft"
    assert len(data["waypoints"]) == len(fallback_candidates)
    for waypoint, candidate in zip(data["waypoints"], fallback_candidates):
        assert waypoint["poi_id"] == candidate["poi_id"]
        assert waypoint["lat"] == candidate["lat"]
        assert waypoint["lng"] == candidate["lng"]
