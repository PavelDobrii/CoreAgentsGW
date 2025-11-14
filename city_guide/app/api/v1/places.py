from __future__ import annotations

import logging
from typing import Literal

from fastapi import APIRouter, Query

from ...core.config import settings
from ...schemas.places import Place
from ...services import google_poi

router = APIRouter(prefix="/v1", tags=["places"])

logger = logging.getLogger(__name__)

DEFAULT_RADIUS = 1000


def _fake_places(*, query: str | None, lat: float | None, lng: float | None) -> list[Place]:
    seed_address = "Downtown"
    address = f"{seed_address}, query={query}" if query else seed_address
    locations = [
        ("1", "Central Park", 40.785091, -73.968285, "park"),
        ("2", "City Museum", 40.779437, -73.963244, "museum"),
        ("3", "Grand Library", 40.753182, -73.982253, "library"),
    ]
    if lat is not None and lng is not None:
        locations[0] = ("1", "Nearby Cafe", lat, lng, "cafe")
    return [
        Place(
            id=item_id,
            name=name,
            address=address,
            location={"lat": item_lat, "lng": item_lng},
            types=[place_type],
            source="mock",
        )
        for item_id, name, item_lat, item_lng, place_type in locations
    ]


@router.get("/places", response_model=list[Place])
async def get_places(
    query: str | None = Query(default=None, description="Text query to search"),
    lat: float | None = Query(default=None, description="Latitude"),
    lng: float | None = Query(default=None, description="Longitude"),
    language: str | None = Query(default=None, description="Preferred response language"),
    place_type: Literal["locality", "country"] | None = Query(
        default=None,
        alias="type",
        description="Result type",
    ),
) -> list[Place]:
    del language, place_type  # currently unused but reserved for future use
    if settings.use_google_sources and lat is not None and lng is not None:
        try:
            raw_places = await google_poi.fetch_places(
                lat=lat,
                lng=lng,
                radius=DEFAULT_RADIUS,
                keyword=query,
            )
            places = [
                Place(
                    id=item.get("poi_id", ""),
                    name=item.get("name", "Unknown"),
                    address="",
                    location={"lat": item.get("lat", 0.0), "lng": item.get("lng", 0.0)},
                    types=[item.get("category")] if item.get("category") else None,
                    source="google_places",
                )
                for item in raw_places
            ]
            if places:
                return places
        except Exception:  # pragma: no cover - defensive logging
            logger.exception("Failed to fetch places from Google")
    return _fake_places(query=query, lat=lat, lng=lng)
