from __future__ import annotations

from pydantic import BaseModel


class Location(BaseModel):
    lat: float
    lng: float


class Place(BaseModel):
    id: str
    name: str
    address: str
    location: Location
    types: list[str] | None = None
    source: str | None = None
