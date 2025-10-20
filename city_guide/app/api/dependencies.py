from __future__ import annotations

import uuid

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.deps import get_db
from ..db.repo import UserProfileRepository
from ..schemas.route import UserRouteContext

DEFAULT_CONTEXT = UserRouteContext(
    user_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
    city="Vilnius",
    language="en",
    travel_style="balanced",
    interests=[],
    transport_mode="walking",
    duration_min=180,
)


def build_default_context(user_id: uuid.UUID) -> UserRouteContext:
    return DEFAULT_CONTEXT.model_copy(update={"user_id": user_id})


async def get_profile_or_default(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> UserRouteContext:
    repo = UserProfileRepository(db)
    profile = await repo.get_profile(user_id)
    if profile is None:
        return build_default_context(user_id)
    context = profile.context or {}
    return build_default_context(user_id).model_copy(update=context.get("user_context", {}))
