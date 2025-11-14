from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class User:
    id: uuid.UUID
    email: str
    password_hash: str
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    country: str | None = None
    city: str | None = None
    language: str = "en"
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class UserProfile:
    user_id: uuid.UUID
    context: dict[str, Any]
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class RoutePoint:
    id: uuid.UUID
    route_id: uuid.UUID
    poi_id: str
    name: str
    lat: float
    lng: float
    category: str
    order_index: int
    eta_min_walk: int | None = None
    eta_min_drive: int | None = None
    listen_sec: int | None = None
    source_poi_id: str | None = None


@dataclass
class RouteDraft:
    id: uuid.UUID
    user_id: uuid.UUID
    city: str
    language: str
    duration_min: int
    transport_mode: str
    status: str
    payload_json: dict[str, Any]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    points: list[RoutePoint] = field(default_factory=list)


class InMemoryDB:
    def __init__(self) -> None:
        self.users: dict[uuid.UUID, User] = {}
        self.users_by_email: dict[str, uuid.UUID] = {}
        self.profiles: dict[uuid.UUID, UserProfile] = {}
        self.route_drafts: dict[uuid.UUID, RouteDraft] = {}
        self.route_contexts: dict[uuid.UUID, dict] = {}
        self.access_tokens: dict[str, uuid.UUID] = {}
        self.refresh_tokens: dict[str, uuid.UUID] = {}

    def reset(self) -> None:
        self.__init__()


DB = InMemoryDB()
