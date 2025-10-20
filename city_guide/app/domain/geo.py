from __future__ import annotations

import math
from typing import Iterable

EARTH_RADIUS_KM = 6371.0

TRANSPORT_SPEED_KMH = {
    "walking": 5.0,
    "bicycling": 15.0,
    "driving": 40.0,
    "transit": 25.0,
}


def haversine_distance_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    lat1_rad, lng1_rad = math.radians(lat1), math.radians(lng1)
    lat2_rad, lng2_rad = math.radians(lat2), math.radians(lng2)
    dlat = lat2_rad - lat1_rad
    dlng = lng2_rad - lng1_rad
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return EARTH_RADIUS_KM * c


def estimate_travel_minutes(distance_km: float, mode: str) -> float:
    speed = TRANSPORT_SPEED_KMH.get(mode, TRANSPORT_SPEED_KMH["walking"])
    if speed <= 0:
        speed = TRANSPORT_SPEED_KMH["walking"]
    return (distance_km / speed) * 60


def compute_eta_minutes(points: Iterable[dict], mode: str) -> list[dict]:
    enriched: list[dict] = []
    prev = None
    for point in points:
        if prev is not None:
            distance_km = haversine_distance_km(prev["lat"], prev["lng"], point["lat"], point["lng"])
            eta = int(estimate_travel_minutes(distance_km, mode))
        else:
            eta = 0
        enriched.append({**point, "eta_min_walk": eta if mode == "walking" else None, "eta_min_drive": eta if mode != "walking" else None})
        prev = point
    return enriched
