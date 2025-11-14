from __future__ import annotations

import logging
from typing import Any, List, TypedDict

import httpx

from app.core.config import settings
from app.schemas.poi import BrainstormedPOI

logger = logging.getLogger(__name__)

TEXT_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
MAX_TEXT_SEARCH_QUERIES = 30


class CandidatePOI(TypedDict, total=False):
    """Represents a POI candidate that can be used by the route generator."""

    poi_id: str
    name: str
    lat: float
    lng: float
    category: str
    place_id: str
    types: list[str]
    rating: float
    source: str
    description: str | None
    priority: float | None


def fetch_places(**_: Any) -> List[CandidatePOI]:  # pragma: no cover - patched in tests
    return []


def _build_query(poi: BrainstormedPOI) -> str:
    parts = [poi.title]
    if poi.city:
        parts.append(poi.city)
    if poi.country:
        parts.append(poi.country)
    return ", ".join(part for part in parts if part)


async def _text_search(
    client: httpx.AsyncClient,
    api_key: str,
    query: str,
    language: str,
) -> list[dict[str, Any]]:
    response = await client.get(
        TEXT_SEARCH_URL,
        params={"query": query, "language": language, "key": api_key},
    )
    response.raise_for_status()
    payload = response.json()
    status = payload.get("status")
    if status not in {"OK", "ZERO_RESULTS"}:
        logger.warning("Google Places text search returned status %s", status)
        return []
    return payload.get("results", [])


def _select_candidate(results: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not results:
        return None

    def _score(item: dict[str, Any]) -> tuple[float, int]:
        rating = float(item.get("rating") or 0.0)
        votes = int(item.get("user_ratings_total") or 0)
        return rating, votes

    return max(results, key=_score)


def _resolve_category(place: dict[str, Any], fallback: BrainstormedPOI) -> str:
    if fallback.category:
        return fallback.category
    types = place.get("types") or []
    if types:
        return types[0]
    return "sight"


def _map_candidate(place: dict[str, Any], poi: BrainstormedPOI) -> CandidatePOI | None:
    geometry = place.get("geometry") or {}
    location = geometry.get("location") or {}
    lat = location.get("lat")
    lng = location.get("lng")
    if lat is None or lng is None:
        return None

    place_id = place.get("place_id") or place.get("id")
    name = place.get("name") or poi.title
    candidate: CandidatePOI = {
        "poi_id": place_id or poi.title,
        "name": name,
        "lat": float(lat),
        "lng": float(lng),
        "category": _resolve_category(place, poi),
        "source": "google_places",
    }
    if place_id:
        candidate["place_id"] = place_id
    types = place.get("types") or []
    if types:
        candidate["types"] = types
    rating = place.get("rating")
    if rating is not None:
        candidate["rating"] = float(rating)
    if poi.description:
        candidate["description"] = poi.description
    if poi.priority is not None:
        candidate["priority"] = poi.priority
    return candidate


async def validate_brainstormed_poi(
    client: httpx.AsyncClient,
    api_key: str,
    items: list[BrainstormedPOI],
    language: str = "en",
    max_queries: int = MAX_TEXT_SEARCH_QUERIES,
) -> list[CandidatePOI]:
    """Validate GPT brainstormed POIs via Google Places Text Search."""

    if not items or not api_key or not settings.use_google_sources:
        return []

    validated: list[CandidatePOI] = []
    for idx, poi in enumerate(items):
        if idx >= max_queries:
            break

        query = _build_query(poi)
        if not query:
            continue

        try:
            candidates = await _text_search(client, api_key, query, language)
        except httpx.HTTPError as exc:  # pragma: no cover - network failure
            logger.warning("Google Places text search failed for %s: %s", query, exc)
            continue

        best = _select_candidate(candidates)
        if not best:
            continue

        candidate = _map_candidate(best, poi)
        if not candidate:
            continue

        validated.append(candidate)

    return validated
