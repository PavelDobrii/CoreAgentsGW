from __future__ import annotations

from pydantic import BaseModel, Field


class Coordinate(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)


class MessageResponse(BaseModel):
    detail: str
