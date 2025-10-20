from __future__ import annotations

import logging
from typing import Any

import httpx
from tenacity import AsyncRetrying, retry_if_exception_type, stop_after_attempt, wait_exponential

from ..core.config import settings

logger = logging.getLogger(__name__)

PLACES_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"


async def fetch_places(*, lat: float, lng: float, radius: int, keyword: str | None = None) -> list[dict[str, Any]]:
    if not settings.google_maps_api_key:
        logger.info("Google Maps API key not configured, returning empty list")
        return []
    params = {
        "key": settings.google_maps_api_key,
        "location": f"{lat},{lng}",
        "radius": radius,
        "opennow": "true" if keyword else None,
    }
    if keyword:
        params["keyword"] = keyword

    async with httpx.AsyncClient(timeout=10.0) as client:
        async for attempt in AsyncRetrying(
            wait=wait_exponential(multiplier=1, max=10),
            stop=stop_after_attempt(3),
            retry=retry_if_exception_type(httpx.HTTPError),
            reraise=True,
        ):
            with attempt:
                response = await client.get(PLACES_URL, params={k: v for k, v in params.items() if v is not None})
                response.raise_for_status()
                payload = response.json()
                results = payload.get("results", [])
                normalized = [
                    {
                        "poi_id": item["place_id"],
                        "name": item.get("name"),
                        "lat": item["geometry"]["location"]["lat"],
                        "lng": item["geometry"]["location"]["lng"],
                        "category": (item.get("types") or ["unknown"])[0],
                        "rating": item.get("rating", 0.0),
                        "open_now": item.get("opening_hours", {}).get("open_now"),
                    }
                    for item in results
                ]
                return normalized
    return []
