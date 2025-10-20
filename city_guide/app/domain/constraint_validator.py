from __future__ import annotations

from typing import Iterable


from ..schemas.route import HardConstraints


class ConstraintViolation(Exception):
    pass


class ConstraintValidator:
    def __init__(self, constraints: HardConstraints) -> None:
        self.constraints = constraints

    def validate_points(self, points: Iterable[dict]) -> list[dict]:
        points_list = list(points)
        min_points = self.constraints.min_points
        max_points = self.constraints.max_points
        if len(points_list) < min_points:
            raise ConstraintViolation(f"At least {min_points} points required")
        if len(points_list) > max_points:
            points_list = points_list[:max_points]
        return points_list

    def validate_duration(self, points: Iterable[dict], duration_min: int) -> list[dict]:
        total = 0
        valid_points = []
        for point in points:
            listen = point.get("listen_sec", 0) / 60
            move = point.get("eta_min_drive") or point.get("eta_min_walk") or 0
            total += listen + move
            if total <= duration_min:
                valid_points.append(point)
            else:
                break
        if not valid_points:
            raise ConstraintViolation("No points fit into provided duration")
        return valid_points

    def validate_open_now(self, points: Iterable[dict]) -> list[dict]:
        if self.constraints.time_window_start is None:
            return list(points)
        return [p for p in points if p.get("open_now", True)]

    def enforce(self, points: Iterable[dict], duration_min: int) -> list[dict]:
        points_checked = self.validate_open_now(points)
        points_checked = self.validate_points(points_checked)
        return self.validate_duration(points_checked, duration_min)
