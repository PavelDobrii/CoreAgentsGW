from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.deps import get_db
from ...core.config import settings
from ...db.repo import RouteDraftRepository
from ...domain.constraint_validator import ConstraintValidator, ConstraintViolation
from ...domain.geo import compute_eta_minutes
from ...domain.route_optimizer import fallback_route
from ...schemas.route import GenerateRouteRequest, RouteDraftResponse, RoutePoint
from ...services.gpt_client import get_gpt_client
from ...services import google_directions, google_poi

router = APIRouter(prefix="/v1", tags=["routes"])


def _build_response(draft, points) -> RouteDraftResponse:
    return RouteDraftResponse(
        route_id=draft.id,
        status=draft.status,
        city=draft.city,
        language=draft.language,
        duration_min=draft.duration_min,
        transport_mode=draft.transport_mode,
        points=[
            RoutePoint(
                poi_id=_parse_uuid(point.poi_id),
                name=point.name,
                lat=point.lat,
                lng=point.lng,
                category=point.category,
                order_index=point.order_index,
                eta_min_walk=point.eta_min_walk,
                eta_min_drive=point.eta_min_drive,
                listen_sec=point.listen_sec,
            )
            for point in points
        ],
        created_at=draft.created_at,
        updated_at=draft.updated_at,
    )


def _parse_uuid(value: str | uuid.UUID) -> uuid.UUID:
    if isinstance(value, uuid.UUID):
        return value
    try:
        return uuid.UUID(str(value))
    except (ValueError, TypeError):
        return uuid.uuid4()


@router.post("/routes:generate", summary="Generate Route", response_model=RouteDraftResponse)
async def generate_route(
    payload: GenerateRouteRequest,
    db: AsyncSession = Depends(get_db),
) -> RouteDraftResponse:
    gpt_client = get_gpt_client()
    repo = RouteDraftRepository(db)

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
    selected = [c for c in candidates if str(c["poi_id"]) in selected_set] or candidates[: payload.hard_constraints.max_points]

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

    draft = await repo.create_draft(
        user_id=payload.user_context.user_id,
        city=payload.user_context.city,
        language=payload.user_context.language,
        duration_min=payload.user_context.duration_min,
        transport_mode=payload.user_context.transport_mode,
        status="draft",
        payload_json=payload_json,
        points=[
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
    await db.commit()
    draft = await repo.get_draft(draft.id)
    if draft is None:
        raise HTTPException(status_code=404, detail="Route not found after creation")
    return _build_response(draft, draft.points)


@router.get("/routes/{route_id}", summary="Get Route", response_model=RouteDraftResponse)
async def get_route(
    route_id: uuid.UUID = Path(..., description="Route identifier"),
    db: AsyncSession = Depends(get_db),
) -> RouteDraftResponse:
    repo = RouteDraftRepository(db)
    draft = await repo.get_draft(route_id)
    if draft is None:
        raise HTTPException(status_code=404, detail="Route not found")
    return _build_response(draft, draft.points)


