from __future__ import annotations

from typing import List


def distance_matrix(points: list[dict], mode: str = "walking") -> List[List[int]]:  # pragma: no cover
    size = len(points)
    return [[0 for _ in range(size)] for _ in range(size)]
