from __future__ import annotations

import uuid

import pytest

from city_guide.app.core import deps
from city_guide.app.db.repo import RouteDraftRepository


class StubGPTClient:
    async def select_poi(self, user_ctx, candidates, k):
        return [c["poi_id"] for c in candidates[:k]]

    async def order_route(self, user_ctx, nodes, matrix):
        return [node["poi_id"] for node in nodes]


@pytest.mark.asyncio
async def test_generate_route_creates_draft(monkeypatch, async_client):
    async def fake_fetch_places(**kwargs):
        base_lat = 54.6872
        base_lng = 25.2797
        results = []
        for idx in range(5):
            results.append(
                {
                    "poi_id": f"place-{idx}",
                    "name": f"Point {idx}",
                    "lat": base_lat + idx * 0.001,
                    "lng": base_lng + idx * 0.001,
                    "category": "museum",
                    "rating": 4.5,
                    "open_now": True,
                }
            )
        return results

    async def fake_distance_matrix(points, mode):
        size = len(points)
        return [[0 for _ in range(size)] for _ in range(size)]

    monkeypatch.setattr("city_guide.app.services.google_poi.fetch_places", fake_fetch_places)
    monkeypatch.setattr("city_guide.app.services.google_directions.distance_matrix", fake_distance_matrix)
    monkeypatch.setattr("city_guide.app.api.v1.routes.get_gpt_client", lambda: StubGPTClient())

    payload = {
        "user_context": {
            "user_id": str(uuid.uuid4()),
            "city": "Vilnius",
            "language": "en",
            "travel_style": "balanced",
            "interests": ["museums"],
            "transport_mode": "walking",
            "duration_min": 180,
        },
        "start_point": {"lat": 54.6872, "lng": 25.2797},
        "hard_constraints": {
            "min_points": 3,
            "max_points": 5,
            "time_window_start": None,
            "must_include_poi_ids": [],
        },
    }

    response = await async_client.post("/v1/routes:generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert 3 <= len(data["points"]) <= 5

    async with deps.SessionLocal() as session:
        repo = RouteDraftRepository(session)
        draft = await repo.get_draft(uuid.UUID(data["route_id"]))
        assert draft is not None
        assert len(draft.points) == len(data["points"])
