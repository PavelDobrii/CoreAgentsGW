from __future__ import annotations

from typing import Iterable

from .geo import haversine_distance_km


def nearest_neighbor_route(point_ids: Iterable[str], distance_matrix: list[list[float]]) -> list[str]:
    points = list(point_ids)
    if not points:
        return []
    remaining = set(range(len(points)))
    current_index = 0
    order = [points[current_index]]
    remaining.remove(current_index)
    while remaining:
        next_index = min(remaining, key=lambda idx: distance_matrix[current_index][idx])
        order.append(points[next_index])
        remaining.remove(next_index)
        current_index = next_index
    return order


def two_opt(order: list[str], distance_lookup: dict[tuple[str, str], float]) -> list[str]:
    improved = True
    while improved:
        improved = False
        for i in range(1, len(order) - 2):
            for j in range(i + 1, len(order)):
                if j - i == 1:
                    continue
                a, b = order[i - 1], order[i]
                c, d = order[j - 1], order[j % len(order)]
                current = distance_lookup[(a, b)] + distance_lookup[(c, d)]
                candidate = distance_lookup[(a, c)] + distance_lookup[(b, d)]
                if candidate < current:
                    order[i:j] = reversed(order[i:j])
                    improved = True
    return order


def build_distance_lookup(points: list[dict]) -> dict[tuple[str, str], float]:
    lookup: dict[tuple[str, str], float] = {}
    for i, src in enumerate(points):
        for j, dst in enumerate(points):
            if i == j:
                lookup[(src["poi_id"], dst["poi_id"])] = 0.0
            else:
                dist = haversine_distance_km(src["lat"], src["lng"], dst["lat"], dst["lng"])
                lookup[(src["poi_id"], dst["poi_id"])] = dist
    return lookup


def fallback_route(points: list[dict]) -> list[dict]:
    if not points:
        return []
    lookup = build_distance_lookup(points)
    order = nearest_neighbor_route([p["poi_id"] for p in points], [
        [lookup[(a["poi_id"], b["poi_id"])] for b in points]
        for a in points
    ])
    order_index = {poi_id: idx for idx, poi_id in enumerate(order)}
    ordered = sorted(points, key=lambda p: order_index[p["poi_id"]])
    optimized_ids = two_opt(order, lookup)
    order_index = {poi_id: idx for idx, poi_id in enumerate(optimized_ids)}
    return sorted(points, key=lambda p: order_index[p["poi_id"]])
