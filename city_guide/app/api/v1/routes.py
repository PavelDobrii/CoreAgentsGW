from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.config import settings
from ...core.deps import get_db
from ...db.models import RouteDraft, RoutePoint as RoutePointModel
from ...db.repo import RouteDraftRepository
from ...domain.constraint_validator import ConstraintValidator, ConstraintViolation
from ...domain.geo import compute_eta_minutes
from ...domain.route_optimizer import fallback_route
from ...schemas.common import Coordinate
from ...schemas.places import Location
from ...schemas.route import GenerateRouteRequest, HardConstraints, UserRouteContext
from ...schemas.trip import (
    GenerateTripOptions,
    GenerateTripResponse,
    TripCreateUpdate,
    TripListResponse,
    TripResponse,
    TripStatus,
    RouteOptions,
    Waypoint,
)
from ...services import google_directions, google_poi
from ...services.gpt_client import get_gpt_client


router = APIRouter(prefix="/v1", tags=["routes"])

CURRENT_USER_ID = uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")


def _get_current_user_id() -> uuid.UUID:
    return CURRENT_USER_ID


@router.get("/routes", response_model=TripListResponse, summary="List Trips")
async def list_trips(db: AsyncSession = Depends(get_db)) -> TripListResponse:
    repo = RouteDraftRepository(db)
    drafts = await repo.list_drafts_for_user(_get_current_user_id())
    return [_trip_response_from_draft(draft) for draft in drafts]


@router.get("/routes/{route_id}", response_model=TripResponse, summary="Get Trip")
async def get_trip(
    route_id: uuid.UUID = Path(..., description="Route identifier"),
    db: AsyncSession = Depends(get_db),
) -> TripResponse:
    repo = RouteDraftRepository(db)
    draft = await repo.get_draft(route_id)
    if draft is None or draft.user_id != _get_current_user_id():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found")
    return _trip_response_from_draft(draft)


@router.post("/routes", response_model=TripResponse, status_code=status.HTTP_201_CREATED, summary="Create Trip")
async def create_trip(
    payload: TripCreateUpdate,
    db: AsyncSession = Depends(get_db),
) -> TripResponse:
    repo = RouteDraftRepository(db)
    duration = _duration_from_options(payload.route_options) or 180
    trip_payload = _merge_trip_payload({}, payload)
    draft = await repo.create_draft(
        user_id=_get_current_user_id(),
        city=payload.locality_id or "unknown",
        language="en",
        duration_min=duration,
        transport_mode="walking",
        status=TripStatus.created.value,
        payload_json=trip_payload,
        points=[],
    )
    await db.commit()
    draft = await repo.get_draft(draft.id)
    if draft is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Route not saved")
    return _trip_response_from_draft(draft)


@router.post("/routes/{route_id}", response_model=TripResponse, summary="Update Trip")
async def update_trip(
    payload: TripCreateUpdate,
    route_id: uuid.UUID = Path(..., description="Route identifier"),
    db: AsyncSession = Depends(get_db),
) -> TripResponse:
    repo = RouteDraftRepository(db)
    draft = await repo.get_draft(route_id)
    if draft is None or draft.user_id != _get_current_user_id():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found")
    duration = _duration_from_options(payload.route_options)
    updated_payload = _merge_trip_payload(draft.payload_json or {}, payload)
    await repo.update_draft(
        route_id,
        city=payload.locality_id or draft.city,
        duration_min=duration if duration is not None else draft.duration_min,
        payload_json=updated_payload,
    )
    await db.commit()
    refreshed = await repo.get_draft(route_id)
    if refreshed is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found after update")
    return _trip_response_from_draft(refreshed)


@router.post("/routes/{route_id}/generate", response_model=GenerateTripResponse, summary="Generate Trip")
async def generate_trip(
    payload: GenerateTripOptions,
    route_id: uuid.UUID = Path(..., description="Route identifier"),
    db: AsyncSession = Depends(get_db),
) -> GenerateTripResponse:
    if payload.id != route_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mismatched identifiers")

    repo = RouteDraftRepository(db)
    draft = await repo.get_draft(route_id)
    if draft is None or draft.user_id != _get_current_user_id():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found")

    generate_request = _build_generate_request_from_draft(draft)
    if generate_request is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing start location")

    await _run_generation(repo, draft, generate_request)

    refreshed = await repo.get_draft(route_id)
    if refreshed is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found")

    updated_payload = dict(refreshed.payload_json or {})
    updated_payload["generateRequest"] = payload.model_dump()
    await repo.update_draft(
        route_id,
        status=TripStatus.draft.value,
        payload_json=updated_payload,
    )
    await db.commit()
    return GenerateTripResponse(message="Generation started")


def _duration_from_options(route_options: RouteOptions | None) -> int | None:
    if route_options and route_options.duration:
        try:
            return int(route_options.duration)
        except (ValueError, TypeError):
            return None
    return None


def _merge_trip_payload(existing: dict[str, Any], payload: TripCreateUpdate) -> dict[str, Any]:
    merged = dict(existing or {})
    merged["title"] = payload.title
    merged["description"] = payload.description
    merged["localityId"] = payload.locality_id
    merged["start"] = payload.start.model_dump(by_alias=True) if payload.start else None
    merged["end"] = payload.end.model_dump(by_alias=True) if payload.end else None
    merged["routeOptions"] = (
        payload.route_options.model_dump(by_alias=True) if payload.route_options else None
    )
    return merged


def _build_generate_request_from_draft(draft: RouteDraft) -> GenerateRouteRequest | None:
    start = (draft.payload_json or {}).get("start")
    if not start or "location" not in start:
        return None
    location = start["location"]
    coordinate = Coordinate(lat=location["lat"], lng=location["lng"])
    route_options = (draft.payload_json or {}).get("routeOptions") or {}
    user_context = UserRouteContext(
        user_id=draft.user_id,
        city=draft.city,
        language=draft.language,
        travel_style="balanced",
        interests=route_options.get("interests", []),
        transport_mode=draft.transport_mode,
        duration_min=draft.duration_min,
    )
    hard_constraints = HardConstraints(
        min_points=3,
        max_points=route_options.get("maxPoints", 5) or 5,
        time_window_start=None,
        must_include_poi_ids=[],
    )
    return GenerateRouteRequest(
        user_context=user_context,
        start_point=coordinate,
        hard_constraints=hard_constraints,
        notes=(draft.payload_json or {}).get("description"),
    )


async def _run_generation(repo: RouteDraftRepository, draft: RouteDraft, payload: GenerateRouteRequest) -> None:
    gpt_client = get_gpt_client()

    candidates = []
    if settings.use_google_sources:
        candidates = await google_poi.fetch_places(
            lat=payload.start_point.lat,
            lng=payload.start_point.lng,
            radius=settings.places_radius_m,
        )

    if not candidates:
        for idx in range(max(payload.hard_constraints.min_points, 3)):
            candidates.append(
                {
                    "poi_id": f"local-{idx}",
                    "name": f"POI {idx}",
                    "lat": payload.start_point.lat + 0.001 * idx,
                    "lng": payload.start_point.lng + 0.001 * idx,
                    "category": "landmark",
                    "rating": 4.5 - idx * 0.1,
                    "open_now": True,
                }
            )

    selected_ids = await gpt_client.select_poi(
        payload.user_context.model_dump(), candidates, payload.hard_constraints.max_points
    )
    selected_set = {str(poi_id) for poi_id in selected_ids}
    selected = [c for c in candidates if str(c["poi_id"]) in selected_set] or candidates[
        : payload.hard_constraints.max_points
    ]

    matrix = await google_directions.distance_matrix(selected, payload.user_context.transport_mode)
    if not matrix:
        matrix = [[0 for _ in selected] for _ in selected]

    order = await gpt_client.order_route(payload.user_context.model_dump(), selected, matrix)
    if len(order) != len(selected):
        ordered = fallback_route(selected)
    else:
        order_index = {poi_id: idx for idx, poi_id in enumerate(order)}
        ordered = sorted(selected, key=lambda item: order_index[item["poi_id"]])

    enriched_points: list[dict] = []
    for point in ordered:
        internal_id = str(uuid.uuid4())
        enriched_points.append({**point, "poi_id": internal_id, "source_poi_id": point["poi_id"]})

    enriched_points = compute_eta_minutes(enriched_points, payload.user_context.transport_mode)

    validator = ConstraintValidator(payload.hard_constraints)
    try:
        validated_points = validator.enforce(enriched_points, payload.user_context.duration_min)
    except ConstraintViolation as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    payload_json = {
        "original_candidates": candidates,
        "ordered_candidates": enriched_points,
        "distance_matrix": matrix,
    }

    await repo.replace_points(
        draft.id,
        [
            {
                "poi_id": point["poi_id"],
                "source_poi_id": point.get("source_poi_id"),
                "name": point["name"],
                "lat": point["lat"],
                "lng": point["lng"],
                "category": point["category"],
                "order_index": idx,
                "eta_min_walk": point.get("eta_min_walk"),
                "eta_min_drive": point.get("eta_min_drive"),
                "listen_sec": point.get("listen_sec", 600),
            }
            for idx, point in enumerate(validated_points)
        ],
    )

    updated_payload = dict(draft.payload_json or {})
    updated_payload["generation"] = payload_json
    await repo.update_draft(
        draft.id,
        status=TripStatus.draft.value,
        transport_mode=payload.user_context.transport_mode,
        duration_min=payload.user_context.duration_min,
        payload_json=updated_payload,
    )


def _trip_response_from_draft(draft: RouteDraft) -> TripResponse:
    payload = draft.payload_json or {}
    points = [_waypoint_from_point_model(point) for point in draft.points]
    start_data = payload.get("start") or (points[0].model_dump(by_alias=True) if points else None)
    end_data = payload.get("end") or (points[-1].model_dump(by_alias=True) if points else None)

    start_waypoint = _ensure_waypoint(start_data)
    end_waypoint = _ensure_waypoint(end_data)

    name = payload.get("title") or payload.get("name") or "Untitled trip"
    route_options = payload.get("routeOptions") or {}

    return TripResponse(
        id=draft.id,
        name=name,
        title=name,
        description=payload.get("description"),
        start_waypoint=start_waypoint,
        end_waypoint=end_waypoint,
        status=_resolve_status(draft.status),
        encoded_polyline=payload.get("encodedPolyline", ""),
        distance=payload.get("distance", 0),
        rating=payload.get("rating", 0),
        waypoints=points or None,
        created_at=draft.created_at,
        updated_at=draft.updated_at,
        locality_id=draft.city,
        duration=draft.duration_min,
        time_of_day=route_options.get("timeOfDay"),
    )


def _waypoint_from_point_model(point: RoutePointModel) -> Waypoint:
    location = Location(lat=point.lat, lng=point.lng)
    return Waypoint(
        id=str(point.poi_id),
        name=point.name,
        address=point.name,
        location=location,
        order=point.order_index,
        source=str(point.source_poi_id) if point.source_poi_id else None,
    )


def _ensure_waypoint(data: Any) -> Waypoint | None:
    if data is None:
        return None
    if isinstance(data, Waypoint):
        return data
    try:
        return Waypoint.model_validate(data)
    except Exception:  # noqa: BLE001
        return None


def _resolve_status(status: str) -> TripStatus:
    try:
        return TripStatus(status)
    except ValueError:
        return TripStatus.draft
