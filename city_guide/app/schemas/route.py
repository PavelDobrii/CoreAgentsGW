from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from .common import Coordinate


class HardConstraints(BaseModel):
    min_points: int = Field(..., ge=1)
    max_points: int = Field(..., ge=1)
    time_window_start: datetime | None = Field(
        default=None,
        description="ISO-время начала экскурсии",
        json_schema_extra={"format": "date-time"},
    )
    must_include_poi_ids: list[uuid.UUID] = Field(default_factory=list)


class UserRouteContext(BaseModel):
    user_id: uuid.UUID
    city: str = Field(..., min_length=1)
    language: str = Field(..., min_length=2, max_length=10)
    travel_style: Literal["relaxed", "balanced", "intense"] = "balanced"
    interests: list[str] = Field(default_factory=list)
    transport_mode: Literal["walking", "bicycling", "driving", "transit"] = "walking"
    duration_min: int = Field(..., ge=30, le=480)


class RoutePoint(BaseModel):
    poi_id: uuid.UUID
    name: str
    lat: float
    lng: float
    category: str
    order_index: int
    eta_min_walk: int | None = None
    eta_min_drive: int | None = None
    listen_sec: int | None = None


class RouteDraftResponse(BaseModel):
    route_id: uuid.UUID
    status: str
    city: str
    language: str
    duration_min: int
    transport_mode: str
    points: list[RoutePoint]
    created_at: datetime
    updated_at: datetime


class GenerateRouteRequest(BaseModel):
    user_context: UserRouteContext
    start_point: Coordinate
    hard_constraints: HardConstraints
    notes: str | None = None


class Suggestion(BaseModel):
    poi_id: uuid.UUID
    distance_m: int
    reason: str
