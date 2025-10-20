from __future__ import annotations

import logging
from typing import Iterable

import httpx
from tenacity import AsyncRetrying, retry_if_exception_type, stop_after_attempt, wait_exponential

from ..core.config import settings

logger = logging.getLogger(__name__)

DISTANCE_MATRIX_URL = "https://maps.googleapis.com/maps/api/distancematrix/json"


async def distance_matrix(points: Iterable[dict], mode: str) -> list[list[float]]:
    points_list = list(points)
    if not points_list:
        return []
    if not settings.google_maps_api_key:
        logger.info("Google Maps API key not configured, returning heuristic distances")
        return [[0 for _ in points_list] for _ in points_list]

    locations = [f"{p['lat']},{p['lng']}" for p in points_list]
    params = {
        "key": settings.google_maps_api_key,
        "origins": "|".join(locations),
        "destinations": "|".join(locations),
        "mode": mode,
        "units": "metric",
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        async for attempt in AsyncRetrying(
            wait=wait_exponential(multiplier=1, max=10),
            stop=stop_after_attempt(3),
            retry=retry_if_exception_type(httpx.HTTPError),
            reraise=True,
        ):
            with attempt:
                response = await client.get(DISTANCE_MATRIX_URL, params=params)
                response.raise_for_status()
                data = response.json()
                rows = data.get("rows", [])
                matrix: list[list[float]] = []
                for row in rows:
                    elements = row.get("elements", [])
                    matrix.append([elem.get("duration", {}).get("value", 0) / 60 for elem in elements])
                return matrix
    return [[0 for _ in points_list] for _ in points_list]
