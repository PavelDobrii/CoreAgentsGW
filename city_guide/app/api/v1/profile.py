from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.deps import get_db
from ...db.repo import UserProfileRepository
from ...schemas.profile import ProfileResponse, ProfileUpdate
from ...schemas.route import UserRouteContext
from ..dependencies import build_default_context

router = APIRouter(prefix="/v1", tags=["profile"])

PROFILE_CONTEXT_KEY = "profile"
PLACEHOLDER_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000042")
DEFAULT_PROFILE_TEMPLATE = ProfileResponse(
    id=PLACEHOLDER_USER_ID,
    email="demo.user@example.com",
    first_name="Demo",
    last_name="User",
    phone="+10000000000",
    country="Lithuania",
    city="Vilnius",
    is_active=True,
    language="en",
    interests=[],
    travel_style="balanced",
)


def build_default_profile(user_id: uuid.UUID) -> ProfileResponse:
    return DEFAULT_PROFILE_TEMPLATE.model_copy(update={"id": user_id})


def load_profile_from_context(context: dict | None, user_id: uuid.UUID) -> ProfileResponse:
    if not context:
        return build_default_profile(user_id)
    data = context.get(PROFILE_CONTEXT_KEY)
    if not data:
        return build_default_profile(user_id)
    return ProfileResponse.model_validate(data)


async def persist_profile(
    repo: UserProfileRepository, *, user_id: uuid.UUID, profile: ProfileResponse, context: dict | None
) -> None:
    snapshot = dict(context or {})
    snapshot[PROFILE_CONTEXT_KEY] = profile.model_dump(by_alias=True, exclude_none=True)
    await repo.upsert_profile(user_id, snapshot)


@router.get("/profile", summary="Get Profile", response_model=ProfileResponse)
async def get_profile(db: AsyncSession = Depends(get_db)) -> ProfileResponse:
    repo = UserProfileRepository(db)
    stored = await repo.get_profile(PLACEHOLDER_USER_ID)
    if stored is None:
        return build_default_profile(PLACEHOLDER_USER_ID)
    return load_profile_from_context(stored.context, PLACEHOLDER_USER_ID)


@router.put("/profile", summary="Update Profile", response_model=ProfileResponse)
async def update_profile(payload: ProfileUpdate, db: AsyncSession = Depends(get_db)) -> ProfileResponse:
    repo = UserProfileRepository(db)
    stored = await repo.get_profile(PLACEHOLDER_USER_ID)
    context = stored.context if stored else {}
    current = load_profile_from_context(context, PLACEHOLDER_USER_ID)
    update_data = payload.model_dump(exclude_unset=True)
    updated = current.model_copy(update=update_data)
    await persist_profile(repo, user_id=PLACEHOLDER_USER_ID, profile=updated, context=context)
    await db.commit()
    return updated


@router.get(
    "/profile/context",
    summary="Get Profile Context",
    response_model=UserRouteContext,
)
async def get_profile_context(
    user_id: uuid.UUID = Query(..., description="User identifier"),
    db: AsyncSession = Depends(get_db),
) -> UserRouteContext:
    repo = UserProfileRepository(db)
    profile = await repo.get_profile(user_id)
    if profile is None:
        return build_default_context(user_id)
    context = profile.context or {}
    return build_default_context(user_id).model_copy(update=context.get("user_context", {}))


@router.post(
    "/profile/context",
    summary="Create Profile Context",
    response_model=UserRouteContext,
    status_code=status.HTTP_201_CREATED,
)
async def create_profile_context(
    payload: UserRouteContext,
    db: AsyncSession = Depends(get_db),
) -> UserRouteContext:
    repo = UserProfileRepository(db)
    context = {"user_context": payload.model_dump(mode="json")}
    stored = await repo.get_profile(payload.user_id)
    if stored and stored.context:
        context = dict(stored.context)
        context["user_context"] = payload.model_dump(mode="json")
    await repo.upsert_profile(payload.user_id, context)
    await db.commit()
    return payload
