from __future__ import annotations

import uuid
from typing import Any

from ...core import deps
from ...db.repo import RouteDraftRepository
from ...http import Application, HTTPException, Request, json_response
from ...services import google_poi


def _normalize_waypoint(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": payload.get("id"),
        "name": payload.get("name"),
        "address": payload.get("address", ""),
        "location": payload.get("location", {}),
    }


def _serialize_draft(draft) -> dict:
    data = dict(draft.payload_json)
    data.setdefault("id", str(draft.id))
    data.setdefault("status", draft.status)
    data.setdefault("waypoints", [point.__dict__ for point in draft.points])
    return data


def get_gpt_client():  # pragma: no cover - patched in tests
    class _Client:
        def select_poi(self, user_ctx, candidates, k):
            return [c["poi_id"] for c in candidates[:k]]

        def order_route(self, user_ctx, nodes, matrix):
            return [node["poi_id"] for node in nodes]

    return _Client()


def register_routes(app: Application) -> None:
    repo = RouteDraftRepository()

    def _require_user(request: Request):
        authorization = request.headers.get("Authorization")
        if not authorization:
            raise HTTPException(401, "Not authenticated")
        return deps.get_current_user(authorization)

    @app.route("POST", "/v1/routes", summary="Create Trip")
    def create_route(request: Request):
        user = _require_user(request)
        payload = request.json or {}
        response = {
            "name": payload.get("title", "Untitled"),
            "description": payload.get("description", ""),
            "localityId": payload.get("localityId", ""),
            "startWaypoint": _normalize_waypoint(payload.get("start", {})),
            "endWaypoint": _normalize_waypoint(payload.get("end", {})),
            "routeOptions": payload.get("routeOptions", {}),
            "status": "created",
        }
        draft = repo.create_draft(
            user_id=user.id,
            city=response["localityId"],
            language="en",
            duration_min=payload.get("duration_min", 180),
            transport_mode="walking",
            status="created",
            payload_json=response,
            points=[],
        )
        response["id"] = str(draft.id)
        return json_response(response, status_code=201)

    @app.route("GET", "/v1/routes", summary="List Trips")
    def list_routes(request: Request):
        user = _require_user(request)
        drafts = repo.list_drafts_for_user(user.id)
        return json_response([_serialize_draft(draft) for draft in drafts])

    @app.route("GET", "/v1/routes/{route_id}", summary="Get Trip")
    def get_route(request: Request):
        user = _require_user(request)
        route_id = request.path_params.get("route_id")
        draft = repo.get_draft(uuid.UUID(route_id))
        if draft is None or draft.user_id != user.id:
            raise HTTPException(404, "Trip not found")
        data = _serialize_draft(draft)
        data["status"] = draft.status
        data["waypoints"] = [point.__dict__ for point in draft.points]
        return json_response(data)

    @app.route("POST", "/v1/routes/{route_id}/generate", summary="Generate Trip")
    def generate_route(request: Request):
        user = _require_user(request)
        route_id = request.path_params.get("route_id")
        draft = repo.get_draft(uuid.UUID(route_id))
        if draft is None or draft.user_id != user.id:
            raise HTTPException(404, "Trip not found")
        base_points = google_poi.fetch_places(city=draft.city)
        if not base_points:
            base_points = [
                {
                    "poi_id": f"poi-{idx}",
                    "name": f"Point {idx}",
                    "lat": 0.0,
                    "lng": 0.0,
                    "category": "sight",
                }
                for idx in range(3)
            ]
        gpt = get_gpt_client()
        selected = gpt.select_poi({}, base_points, k=min(3, len(base_points)))
        ordered = gpt.order_route({}, [p for p in base_points if p["poi_id"] in selected], [])
        waypoints = [
            {
                "poi_id": poi_id,
                "name": next((p["name"] for p in base_points if p["poi_id"] == poi_id), poi_id),
                "lat": next((p["lat"] for p in base_points if p["poi_id"] == poi_id), 0.0),
                "lng": next((p["lng"] for p in base_points if p["poi_id"] == poi_id), 0.0),
                "category": "sight",
            }
            for poi_id in ordered
        ]
        repo.replace_points(draft.id, waypoints)
        repo.update_draft(draft.id, status="draft")
        draft.payload_json["status"] = "draft"
        draft.payload_json["waypoints"] = waypoints
        return json_response({"message": "Generation started"})
