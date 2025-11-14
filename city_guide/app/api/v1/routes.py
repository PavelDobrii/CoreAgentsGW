from __future__ import annotations

import asyncio
import logging
import uuid
from typing import Any

from ...core import deps
from ...core.config import settings
from ...db.repo import RouteDraftRepository, UserProfileRepository
from ...http import Application, HTTPException, Request, json_response
from ...schemas.places import Location
from ...schemas.poi import BrainstormPOIRequest
from ...services import google_poi
from ...services.gpt_client import GPTClient

logger = logging.getLogger(__name__)

MAX_WAYPOINTS = 3


def _normalize_waypoint(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": payload.get("id"),
        "name": payload.get("name"),
        "address": payload.get("address", ""),
        "location": payload.get("location", {}),
    }


def _serialize_point(point) -> dict[str, Any]:
    return {
        "id": str(point.id),
        "poi_id": point.poi_id,
        "name": point.name,
        "lat": point.lat,
        "lng": point.lng,
        "category": point.category,
        "order_index": point.order_index,
        "eta_min_walk": point.eta_min_walk,
        "eta_min_drive": point.eta_min_drive,
        "listen_sec": point.listen_sec,
        "source_poi_id": point.source_poi_id,
    }


def _serialize_draft(draft) -> dict:
    data = dict(draft.payload_json)
    data.setdefault("id", str(draft.id))
    data.setdefault("status", draft.status)
    data.setdefault("waypoints", [_serialize_point(point) for point in draft.points])
    return data


def get_gpt_client() -> GPTClient:  # pragma: no cover - patched in tests
    return GPTClient()


def _start_location_from_payload(payload: dict[str, Any]) -> Location | None:
    waypoint = payload.get("startWaypoint") or payload.get("start") or {}
    location = waypoint.get("location") or {}
    lat = location.get("lat")
    lng = location.get("lng")
    if lat is None or lng is None:
        return None
    try:
        return Location(lat=float(lat), lng=float(lng))
    except (TypeError, ValueError):  # pragma: no cover - defensive conversion
        return None


def _build_brainstorm_request(
    draft,
    payload: dict[str, Any],
    user_context: dict[str, Any] | None,
) -> BrainstormPOIRequest:
    return BrainstormPOIRequest(
        locality_id=payload.get("localityId") or draft.city,
        start_location=_start_location_from_payload(payload),
        user_context=user_context,
        route_options=payload.get("routeOptions"),
    )


def _fallback_candidates(city: str, payload: dict[str, Any]) -> list[google_poi.CandidatePOI]:
    start_location = _start_location_from_payload(payload)
    base_lat = start_location.lat if start_location else 0.0
    base_lng = start_location.lng if start_location else 0.0
    return [
        {
            "poi_id": f"fallback-{city}-{idx}",
            "name": f"Point {idx}",
            "lat": base_lat + idx * 0.001,
            "lng": base_lng + idx * 0.001,
            "category": "sight",
            "source": "fallback",
        }
        for idx in range(MAX_WAYPOINTS)
    ]


def _candidate_to_waypoint(candidate: google_poi.CandidatePOI, order_index: int) -> dict[str, Any]:
    return {
        "poi_id": candidate.get("poi_id"),
        "name": candidate.get("name", candidate.get("poi_id")),
        "lat": float(candidate.get("lat", 0.0)),
        "lng": float(candidate.get("lng", 0.0)),
        "category": candidate.get("category", "sight"),
        "order_index": order_index,
        "source_poi_id": candidate.get("place_id"),
    }


async def _brainstorm_candidates(
    draft,
    payload: dict[str, Any],
    user_context: dict[str, Any] | None,
    gpt: GPTClient,
) -> tuple[list[google_poi.CandidatePOI], int, int]:
    request = _build_brainstorm_request(draft, payload, user_context)
    try:
        response = await gpt.brainstorm_poi(request)
    except AttributeError:
        response = None
    brainstorm_count = len(response.items) if response else 0

    validated: list[google_poi.CandidatePOI] = []
    httpx_module = getattr(google_poi, "httpx", None)
    if (
        response
        and response.items
        and settings.use_google_sources
        and settings.google_maps_api_key
        and httpx_module is not None
    ):
        async with httpx_module.AsyncClient(timeout=10) as http_client:
            validated = await google_poi.validate_brainstormed_poi(
                client=http_client,
                api_key=settings.google_maps_api_key,
                items=response.items,
                language=draft.language or "en",
            )

    logger.info(
        "Route %s: GPT brainstorm produced %d POIs", str(draft.id), brainstorm_count
    )
    logger.info(
        "Route %s: %d POIs validated via Google", str(draft.id), len(validated)
    )

    if validated:
        return validated, brainstorm_count, len(validated)

    fallback = google_poi.fetch_places(city=draft.city) or []
    if not fallback:
        fallback = _fallback_candidates(draft.city, payload)
    return fallback, brainstorm_count, len(validated)


async def _select_and_order(
    gpt: GPTClient,
    user_context: dict[str, Any] | None,
    candidates: list[google_poi.CandidatePOI],
    limit: int = MAX_WAYPOINTS,
) -> list[google_poi.CandidatePOI]:
    if not candidates:
        return []
    k = min(limit, len(candidates))
    try:
        selected_ids = await gpt.select_poi(user_context or {}, candidates, k)
    except AttributeError:
        selected_ids = []
    if not selected_ids:
        selected_candidates = candidates[:k]
    else:
        selected_candidates: list[google_poi.CandidatePOI] = [
            candidate for candidate in candidates if candidate.get("poi_id") in selected_ids
        ]
        if len(selected_candidates) < k:
            for candidate in candidates:
                if candidate not in selected_candidates:
                    selected_candidates.append(candidate)
                if len(selected_candidates) == k:
                    break

    try:
        ordered_ids = await gpt.order_route(user_context or {}, selected_candidates, [])
    except AttributeError:
        ordered_ids = []
    if not ordered_ids:
        return selected_candidates

    mapping = {candidate.get("poi_id"): candidate for candidate in selected_candidates}
    ordered: list[google_poi.CandidatePOI] = []
    for poi_id in ordered_ids:
        candidate = mapping.get(poi_id)
        if candidate:
            ordered.append(candidate)
    for candidate in selected_candidates:
        if candidate not in ordered:
            ordered.append(candidate)
    return ordered


async def _run_generation(
    draft,
    payload: dict[str, Any],
    user_context: dict[str, Any] | None,
    gpt: GPTClient,
) -> list[dict[str, Any]]:
    candidates, brainstorm_count, validated_count = await _brainstorm_candidates(
        draft, payload, user_context, gpt
    )
    ordered_candidates = await _select_and_order(gpt, user_context, candidates)
    waypoints = [
        _candidate_to_waypoint(candidate, idx)
        for idx, candidate in enumerate(ordered_candidates)
    ]
    logger.info(
        "Route %s: final POI count after selection %d",
        str(draft.id),
        len(waypoints),
    )
    return waypoints


def register_routes(app: Application) -> None:
    repo = RouteDraftRepository()
    profiles = UserProfileRepository()

    def _require_user(request: Request):
        authorization = request.headers.get("authorization")
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
        data["waypoints"] = [_serialize_point(point) for point in draft.points]
        return json_response(data)

    @app.route("POST", "/v1/routes/{route_id}/generate", summary="Generate Trip")
    def generate_route(request: Request):
        user = _require_user(request)
        route_id = request.path_params.get("route_id")
        draft = repo.get_draft(uuid.UUID(route_id))
        if draft is None or draft.user_id != user.id:
            raise HTTPException(404, "Trip not found")
        payload = dict(draft.payload_json)
        profile = profiles.get_profile(user.id)
        user_context = profile.context if profile else None
        gpt = get_gpt_client()
        try:
            waypoints = asyncio.run(_run_generation(draft, payload, user_context, gpt))
        except Exception as exc:  # noqa: BLE001
            logger.exception("Route generation failed for %s: %s", route_id, exc)
            raise HTTPException(500, "Failed to generate trip") from exc
        if not waypoints:
            fallback = _fallback_candidates(draft.city, payload)
            waypoints = [
                _candidate_to_waypoint(candidate, idx) for idx, candidate in enumerate(fallback)
            ]
        repo.replace_points(draft.id, waypoints)
        updated_payload = dict(draft.payload_json)
        updated_payload["status"] = "draft"
        updated_payload["waypoints"] = waypoints
        repo.update_draft(draft.id, status="draft", payload_json=updated_payload)
        return json_response({"message": "Generation started"})
