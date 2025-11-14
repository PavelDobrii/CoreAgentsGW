from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from .places import Location


class BrainstormedPOI(BaseModel):
    """Represents a single GPT-proposed point of interest."""

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    title: str
    city: str | None = None
    country: str | None = None
    category: str | None = None
    description: str | None = None
    priority: float | None = None


class BrainstormPOIRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    locality_id: str | None = Field(default=None, alias="localityId")
    start_location: Location | None = Field(default=None, alias="startLocation")
    user_context: dict[str, Any] | None = Field(default=None, alias="userContext")
    route_options: dict[str, Any] | None = Field(default=None, alias="routeOptions")


class BrainstormPOIResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    items: list[BrainstormedPOI]
