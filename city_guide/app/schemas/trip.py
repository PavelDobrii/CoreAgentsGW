from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from .places import Location


class TripStatus(str, Enum):
    created = "created"
    draft = "draft"
    in_progress = "inProgress"
    success = "success"
    failed = "failed"


class Waypoint(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: str | None = None
    name: str
    address: str
    location: Location
    description: str | None = None
    audio_src: str | None = Field(default=None, alias="audioSrc")
    poster_src: str | None = Field(default=None, alias="posterSrc")
    text: str | None = None
    order: int | None = None
    types: list[str] | None = None
    source: str | None = None


class RouteOptions(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    interests: list[str] | None = None
    moods: list[str] | None = None
    date_at: str | None = Field(default=None, alias="dateAt")
    duration: str | None = None
    time_of_day: str | None = Field(default=None, alias="timeOfDay")


class TripResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: uuid.UUID
    name: str = Field(default="Untitled trip")
    title: str | None = Field(default=None, alias="title")
    description: str | None = None
    start_waypoint: Waypoint | None = Field(default=None, alias="startWaypoint")
    end_waypoint: Waypoint | None = Field(default=None, alias="endWaypoint")
    status: TripStatus = TripStatus.created
    encoded_polyline: str = Field(default="", alias="encodedPolyline")
    distance: float = 0
    rating: float = 0
    waypoints: list[Waypoint] | None = None
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    locality_id: str | None = Field(default=None, alias="localityId")
    duration: int | None = None
    time_of_day: str | None = Field(default=None, alias="timeOfDay")


TripListResponse = list[TripResponse]


class TripCreateUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: uuid.UUID | None = None
    title: str = Field(default="Untitled trip")
    description: str | None = None
    locality_id: str | None = Field(default=None, alias="localityId")
    start: Waypoint | None = None
    end: Waypoint | None = None
    route_options: RouteOptions | None = Field(default=None, alias="routeOptions")


class GenerateTripOptions(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: uuid.UUID
    waypoints: list[str] = Field(default_factory=list)
    places: list[str] = Field(default_factory=list)


class GenerateTripResponse(BaseModel):
    message: str
