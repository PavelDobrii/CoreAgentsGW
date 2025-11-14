from __future__ import annotations

import uuid
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ProfileResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: uuid.UUID
    email: str
    first_name: str = Field(alias="firstName")
    last_name: str = Field(alias="lastName")
    phone: str
    country: str
    city: str
    is_active: bool = Field(alias="isActive")
    language: str
    gender: Literal["male", "female"] | None = None
    age: int | None = None
    region: str | None = None
    interests: list[str] | None = None
    travel_style: str | None = Field(default=None, alias="travelStyle")


class ProfileUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    gender: Literal["male", "female"] | None = None
    age: int | None = None
    city: str | None = None
    language: str | None = None
    region: str | None = None
    interests: list[str] | None = None
    travel_style: str | None = Field(default=None, alias="travelStyle")
