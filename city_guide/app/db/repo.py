from __future__ import annotations

import uuid
from typing import Sequence

from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from .models import RouteDraft, RoutePoint, UserProfile


class UserProfileRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def upsert_profile(self, user_id: uuid.UUID, context: dict) -> UserProfile:
        profile = await self.session.get(UserProfile, user_id)
        if profile is None:
            profile = UserProfile(user_id=user_id, context=context)
            self.session.add(profile)
        else:
            profile.context = context
        await self.session.flush()
        return profile

    async def get_profile(self, user_id: uuid.UUID) -> UserProfile | None:
        return await self.session.get(UserProfile, user_id)


class RouteDraftRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_draft(
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
            user_id=user_id,
            city=city,
            language=language,
            duration_min=duration_min,
            transport_mode=transport_mode,
            status=status,
            payload_json=payload_json,
        )
        self.session.add(draft)
        await self.session.flush()

        for order_index, point in enumerate(points):
            route_point = RoutePoint(
                route_id=draft.id,
                poi_id=str(point["poi_id"]),
                name=point["name"],
                lat=point["lat"],
                lng=point["lng"],
                category=point.get("category", "unknown"),
                order_index=point.get("order_index", order_index),
                eta_min_walk=point.get("eta_min_walk"),
                eta_min_drive=point.get("eta_min_drive"),
                listen_sec=point.get("listen_sec"),
                source_poi_id=point.get("source_poi_id"),
            )
            self.session.add(route_point)
        await self.session.flush()
        await self.session.refresh(draft)
        return draft

    async def get_draft(self, route_id: uuid.UUID) -> RouteDraft | None:
        stmt = select(RouteDraft).options(selectinload(RouteDraft.points)).where(RouteDraft.id == route_id)
        result = await self.session.execute(stmt)
        draft = result.scalars().first()
        return draft

    async def list_drafts_for_user(self, user_id: uuid.UUID) -> list[RouteDraft]:
        stmt = (
            select(RouteDraft)
            .options(selectinload(RouteDraft.points))
            .where(RouteDraft.user_id == user_id)
            .order_by(RouteDraft.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars())

    async def update_draft(
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
        draft = await self.session.get(RouteDraft, route_id)
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
        await self.session.flush()
        await self.session.refresh(draft)
        return draft

    async def replace_points(self, route_id: uuid.UUID, points: Sequence[dict]) -> None:
        await self.session.execute(delete(RoutePoint).where(RoutePoint.route_id == route_id))
        for order_index, point in enumerate(points):
            route_point = RoutePoint(
                route_id=route_id,
                poi_id=str(point["poi_id"]),
                name=point["name"],
                lat=point["lat"],
                lng=point["lng"],
                category=point.get("category", "unknown"),
                order_index=point.get("order_index", order_index),
                eta_min_walk=point.get("eta_min_walk"),
                eta_min_drive=point.get("eta_min_drive"),
                listen_sec=point.get("listen_sec"),
                source_poi_id=point.get("source_poi_id"),
            )
            self.session.add(route_point)
        await self.session.flush()

    async def list_points(self, route_id: uuid.UUID) -> list[RoutePoint]:
        stmt = select(RoutePoint).where(RoutePoint.route_id == route_id).order_by(RoutePoint.order_index)
        result = await self.session.execute(stmt)
        return list(result.scalars())
