from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any, Sequence

from . import database
from .entities import RouteDraft, RoutePoint, User, UserProfile


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_datetime(value) -> datetime:
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value))


def _parse_json(value):
    if isinstance(value, (dict, list)):
        return value
    if value is None:
        return {}
    return json.loads(value)


class UserRepository:
    def get_by_email(self, email: str) -> User | None:
        row = database.execute(
            "SELECT * FROM users WHERE email = :email",
            {"email": email.lower()},
            fetchone=True,
        )
        if row is None:
            return None
        return self._row_to_user(row)

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        row = database.execute(
            "SELECT * FROM users WHERE id = :id",
            {"id": str(user_id)},
            fetchone=True,
        )
        if row is None:
            return None
        return self._row_to_user(row)

    def _row_to_user(self, row: dict) -> User:
        return User(
            id=uuid.UUID(row["id"]),
            email=row["email"],
            password_hash=row["password_hash"],
            first_name=row.get("first_name"),
            last_name=row.get("last_name"),
            phone=row.get("phone"),
            country=row.get("country"),
            city=row.get("city"),
            language=row.get("language", "en"),
            is_active=bool(row.get("is_active", True)),
            created_at=_parse_datetime(row.get("created_at")),
            updated_at=_parse_datetime(row.get("updated_at")),
        )

    def _verify_user_persisted(self, user_id: uuid.UUID) -> None:
        row = database.execute(
            "SELECT id FROM users WHERE id = :id",
            {"id": str(user_id)},
            fetchone=True,
        )
        if row is None:
            raise RuntimeError("Database write verification failed for user %s" % user_id)

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
        user_id = uuid.uuid4()
        now = _now().isoformat()
        database.execute(
            """
            INSERT INTO users (
                id, email, password_hash, first_name, last_name,
                phone, country, city, language, is_active, created_at, updated_at
            ) VALUES (
                :id, :email, :password_hash, :first_name, :last_name,
                :phone, :country, :city, :language, :is_active, :created_at, :updated_at
            )
            """,
            {
                "id": str(user_id),
                "email": email.lower(),
                "password_hash": password_hash,
                "first_name": first_name,
                "last_name": last_name,
                "phone": phone,
                "country": country,
                "city": city,
                "language": (language or "en"),
                "is_active": True,
                "created_at": now,
                "updated_at": now,
            },
        )
        self._verify_user_persisted(user_id)
        created = self.get_by_id(user_id)
        if created is None:  # pragma: no cover - defensive
            raise RuntimeError("Failed to load persisted user %s" % user_id)
        return created

    def save_user(self, user: User) -> User:
        now = _now().isoformat()
        database.execute(
            """
            UPDATE users SET
                email = :email,
                first_name = :first_name,
                last_name = :last_name,
                phone = :phone,
                country = :country,
                city = :city,
                language = :language,
                is_active = :is_active,
                updated_at = :updated_at
            WHERE id = :id
            """,
            {
                "id": str(user.id),
                "email": user.email.lower(),
                "first_name": user.first_name,
                "last_name": user.last_name,
                "phone": user.phone,
                "country": user.country,
                "city": user.city,
                "language": user.language,
                "is_active": user.is_active,
                "updated_at": now,
            },
        )
        updated = self.get_by_id(user.id)
        if updated is None:
            raise RuntimeError("Failed to update user %s" % user.id)
        return updated


class UserProfileRepository:
    def upsert_profile(self, user_id: uuid.UUID, context: dict) -> UserProfile:
        payload = json.dumps(context)
        now = _now().isoformat()
        existing = self.get_profile(user_id)
        if existing is None:
            database.execute(
                """
                INSERT INTO user_profiles (user_id, context, updated_at)
                VALUES (:user_id, :context, :updated_at)
                """,
                {"user_id": str(user_id), "context": payload, "updated_at": now},
            )
        else:
            database.execute(
                """
                UPDATE user_profiles SET context = :context, updated_at = :updated_at
                WHERE user_id = :user_id
                """,
                {"user_id": str(user_id), "context": payload, "updated_at": now},
            )
        stored = self.get_profile(user_id)
        if stored is None:  # pragma: no cover - defensive
            raise RuntimeError("Failed to persist profile for %s" % user_id)
        return stored

    def get_profile(self, user_id: uuid.UUID) -> UserProfile | None:
        row = database.execute(
            "SELECT * FROM user_profiles WHERE user_id = :user_id",
            {"user_id": str(user_id)},
            fetchone=True,
        )
        if row is None:
            return None
        return UserProfile(
            user_id=uuid.UUID(row["user_id"]),
            context=_parse_json(row.get("context")),
            updated_at=_parse_datetime(row.get("updated_at")),
        )


class RouteDraftRepository:
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
        draft_id = uuid.uuid4()
        now = _now().isoformat()
        database.execute(
            """
            INSERT INTO route_drafts (
                id, user_id, city, language, duration_min,
                transport_mode, status, payload_json, created_at, updated_at
            ) VALUES (
                :id, :user_id, :city, :language, :duration_min,
                :transport_mode, :status, :payload_json, :created_at, :updated_at
            )
            """,
            {
                "id": str(draft_id),
                "user_id": str(user_id),
                "city": city,
                "language": language,
                "duration_min": duration_min,
                "transport_mode": transport_mode,
                "status": status,
                "payload_json": json.dumps(payload_json),
                "created_at": now,
                "updated_at": now,
            },
        )
        self._insert_points(draft_id, points)
        draft = self.get_draft(draft_id)
        if draft is None:
            raise RuntimeError("Failed to create draft %s" % draft_id)
        return draft

    def _insert_points(self, route_id: uuid.UUID, points: Sequence[dict]) -> None:
        for idx, point in enumerate(points):
            database.execute(
                """
                INSERT INTO route_points (
                    id, route_id, poi_id, name, lat, lng, category,
                    order_index, eta_min_walk, eta_min_drive, listen_sec, source_poi_id
                ) VALUES (
                    :id, :route_id, :poi_id, :name, :lat, :lng, :category,
                    :order_index, :eta_min_walk, :eta_min_drive, :listen_sec, :source_poi_id
                )
                """,
                {
                    "id": str(uuid.uuid4()),
                    "route_id": str(route_id),
                    "poi_id": str(point["poi_id"]),
                    "name": point["name"],
                    "lat": float(point["lat"]),
                    "lng": float(point["lng"]),
                    "category": point.get("category", "unknown"),
                    "order_index": point.get("order_index", idx),
                    "eta_min_walk": point.get("eta_min_walk"),
                    "eta_min_drive": point.get("eta_min_drive"),
                    "listen_sec": point.get("listen_sec"),
                    "source_poi_id": point.get("source_poi_id"),
                },
            )

    def _row_to_draft(self, row: dict, points: list[RoutePoint]) -> RouteDraft:
        return RouteDraft(
            id=uuid.UUID(row["id"]),
            user_id=uuid.UUID(row["user_id"]),
            city=row["city"],
            language=row["language"],
            duration_min=int(row["duration_min"]),
            transport_mode=row["transport_mode"],
            status=row["status"],
            payload_json=_parse_json(row.get("payload_json")),
            created_at=_parse_datetime(row.get("created_at")),
            updated_at=_parse_datetime(row.get("updated_at")),
            points=points,
        )

    def _fetch_points(self, route_id: uuid.UUID) -> list[RoutePoint]:
        rows = database.execute(
            "SELECT * FROM route_points WHERE route_id = :route_id ORDER BY order_index",
            {"route_id": str(route_id)},
            fetchall=True,
        )
        return [
            RoutePoint(
                id=uuid.UUID(row["id"]),
                route_id=uuid.UUID(row["route_id"]),
                poi_id=row["poi_id"],
                name=row["name"],
                lat=float(row["lat"]),
                lng=float(row["lng"]),
                category=row["category"],
                order_index=int(row["order_index"]),
                eta_min_walk=row.get("eta_min_walk"),
                eta_min_drive=row.get("eta_min_drive"),
                listen_sec=row.get("listen_sec"),
                source_poi_id=row.get("source_poi_id"),
            )
            for row in rows
        ]

    def get_draft(self, route_id: uuid.UUID) -> RouteDraft | None:
        row = database.execute(
            "SELECT * FROM route_drafts WHERE id = :id",
            {"id": str(route_id)},
            fetchone=True,
        )
        if row is None:
            return None
        points = self._fetch_points(route_id)
        return self._row_to_draft(row, points)

    def list_drafts_for_user(self, user_id: uuid.UUID) -> list[RouteDraft]:
        rows = database.execute(
            "SELECT * FROM route_drafts WHERE user_id = :user_id ORDER BY created_at DESC",
            {"user_id": str(user_id)},
            fetchall=True,
        )
        drafts: list[RouteDraft] = []
        for row in rows:
            route_id = uuid.UUID(row["id"])
            points = self._fetch_points(route_id)
            drafts.append(self._row_to_draft(row, points))
        return drafts

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
        fields: list[str] = []
        params: dict[str, Any] = {"id": str(route_id)}
        if city is not None:
            fields.append("city = :city")
            params["city"] = city
        if language is not None:
            fields.append("language = :language")
            params["language"] = language
        if duration_min is not None:
            fields.append("duration_min = :duration_min")
            params["duration_min"] = duration_min
        if transport_mode is not None:
            fields.append("transport_mode = :transport_mode")
            params["transport_mode"] = transport_mode
        if status is not None:
            fields.append("status = :status")
            params["status"] = status
        if payload_json is not None:
            fields.append("payload_json = :payload_json")
            params["payload_json"] = json.dumps(payload_json)
        if not fields:
            return self.get_draft(route_id)
        fields.append("updated_at = :updated_at")
        params["updated_at"] = _now().isoformat()
        database.execute(
            f"UPDATE route_drafts SET {', '.join(fields)} WHERE id = :id",
            params,
        )
        return self.get_draft(route_id)

    def replace_points(self, route_id: uuid.UUID, points: Sequence[dict]) -> None:
        database.execute(
            "DELETE FROM route_points WHERE route_id = :route_id",
            {"route_id": str(route_id)},
        )
        if points:
            self._insert_points(route_id, points)

    def list_points(self, route_id: uuid.UUID) -> list[RoutePoint]:
        return self._fetch_points(route_id)
