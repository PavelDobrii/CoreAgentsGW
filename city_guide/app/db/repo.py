from __future__ import annotations

import uuid
from dataclasses import replace
from typing import Sequence

from .models import DB, RouteDraft, RoutePoint, User, UserProfile


class UserRepository:
    def __init__(self) -> None:
        self._db = DB

    def get_by_email(self, email: str) -> User | None:
        user_id = self._db.users_by_email.get(email.lower())
        if user_id is None:
            return None
        return self._db.users.get(user_id)

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return self._db.users.get(user_id)

    def create_user(
        self,
        *,
        email: str,
        password_hash: str,
        first_name: str | None = None,
        last_name: str | None = None,
        phone: str | None = None,
        country: str | None = None,
        city: str | None = None,
        language: str | None = "en",
    ) -> User:
        user = User(
            id=uuid.uuid4(),
            email=email.lower(),
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            country=country,
            city=city,
            language=language or "en",
        )
        self._db.users[user.id] = user
        self._db.users_by_email[user.email] = user.id
        return user

    def save_user(self, user: User) -> None:
        self._db.users[user.id] = user
        self._db.users_by_email[user.email] = user.id


class UserProfileRepository:
    def __init__(self) -> None:
        self._db = DB

    def upsert_profile(self, user_id: uuid.UUID, context: dict) -> UserProfile:
        profile = self._db.profiles.get(user_id)
        if profile is None:
            profile = UserProfile(user_id=user_id, context=context)
        else:
            profile = replace(profile, context=context)
        self._db.profiles[user_id] = profile
        return profile

    def get_profile(self, user_id: uuid.UUID) -> UserProfile | None:
        return self._db.profiles.get(user_id)


class RouteDraftRepository:
    def __init__(self) -> None:
        self._db = DB

    def create_draft(
        self,
        *,
        user_id: uuid.UUID,
        city: str,
        language: str,
        duration_min: int,
        transport_mode: str,
        status: str,
        payload_json: dict,
        points: Sequence[dict],
    ) -> RouteDraft:
        draft = RouteDraft(
            id=uuid.uuid4(),
            user_id=user_id,
            city=city,
            language=language,
            duration_min=duration_min,
            transport_mode=transport_mode,
            status=status,
            payload_json=payload_json,
        )
        draft.points = [
            RoutePoint(
                id=uuid.uuid4(),
                route_id=draft.id,
                poi_id=str(point["poi_id"]),
                name=point["name"],
                lat=point["lat"],
                lng=point["lng"],
                category=point.get("category", "unknown"),
                order_index=point.get("order_index", idx),
                eta_min_walk=point.get("eta_min_walk"),
                eta_min_drive=point.get("eta_min_drive"),
                listen_sec=point.get("listen_sec"),
                source_poi_id=point.get("source_poi_id"),
            )
            for idx, point in enumerate(points)
        ]
        self._db.route_drafts[draft.id] = draft
        return draft

    def get_draft(self, route_id: uuid.UUID) -> RouteDraft | None:
        return self._db.route_drafts.get(route_id)

    def list_drafts_for_user(self, user_id: uuid.UUID) -> list[RouteDraft]:
        return [draft for draft in self._db.route_drafts.values() if draft.user_id == user_id]

    def update_draft(
        self,
        route_id: uuid.UUID,
        *,
        city: str | None = None,
        language: str | None = None,
        duration_min: int | None = None,
        transport_mode: str | None = None,
        status: str | None = None,
        payload_json: dict | None = None,
    ) -> RouteDraft | None:
        draft = self._db.route_drafts.get(route_id)
        if draft is None:
            return None
        if city is not None:
            draft.city = city
        if language is not None:
            draft.language = language
        if duration_min is not None:
            draft.duration_min = duration_min
        if transport_mode is not None:
            draft.transport_mode = transport_mode
        if status is not None:
            draft.status = status
        if payload_json is not None:
            draft.payload_json = payload_json
        return draft

    def replace_points(self, route_id: uuid.UUID, points: Sequence[dict]) -> None:
        draft = self._db.route_drafts.get(route_id)
        if draft is None:
            return
        draft.points = [
            RoutePoint(
                id=uuid.uuid4(),
                route_id=route_id,
                poi_id=str(point["poi_id"]),
                name=point["name"],
                lat=point["lat"],
                lng=point["lng"],
                category=point.get("category", "unknown"),
                order_index=point.get("order_index", idx),
                eta_min_walk=point.get("eta_min_walk"),
                eta_min_drive=point.get("eta_min_drive"),
                listen_sec=point.get("listen_sec"),
                source_poi_id=point.get("source_poi_id"),
            )
            for idx, point in enumerate(points)
        ]

    def list_points(self, route_id: uuid.UUID) -> list[RoutePoint]:
        draft = self._db.route_drafts.get(route_id)
        if draft is None:
            return []
        return list(draft.points)
