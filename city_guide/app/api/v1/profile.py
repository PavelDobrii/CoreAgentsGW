from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.deps import get_db
from ...db.repo import UserProfileRepository
from ...schemas.route import UserRouteContext
from ..dependencies import build_default_context

router = APIRouter(prefix="/v1", tags=["profile"])


@router.get("/profile", summary="Get Profile", response_model=UserRouteContext)
async def get_profile(
    user_id: uuid.UUID = Query(..., description="User identifier"),
    db=Depends(get_db),
) -> UserRouteContext:
    repo = UserProfileRepository(db)
    profile = await repo.get_profile(user_id)
    if profile is None:
        return build_default_context(user_id)
    context = profile.context or {}
    merged = build_default_context(user_id).model_copy(update=context.get("user_context", {}))
    return merged


@router.post(
    "/profile",
    summary="Create Profile",
    response_model=UserRouteContext,
    status_code=status.HTTP_201_CREATED,
)
async def create_profile(
    payload: UserRouteContext,
    db: AsyncSession = Depends(get_db),
) -> UserRouteContext:
    repo = UserProfileRepository(db)
    context = {"user_context": payload.model_dump(mode="json")}
    await repo.upsert_profile(payload.user_id, context)
    await db.commit()
    return payload
