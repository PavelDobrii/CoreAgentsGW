from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.deps import get_current_user, get_db
from ...db.models import User
from ...db.repo import UserProfileRepository
from ...schemas.profile import ProfileResponse, ProfileUpdate
from ...schemas.route import UserRouteContext
from ..dependencies import build_default_context

router = APIRouter(prefix="/v1", tags=["profile"])

PROFILE_CONTEXT_KEY = "profile"


def build_default_profile(user: User) -> ProfileResponse:
    return ProfileResponse(
        id=user.id,
        email=user.email,
        first_name=user.first_name or "",
        last_name=user.last_name or "",
        phone=user.phone or "",
        country=user.country or "",
        city=user.city or "",
        is_active=user.is_active,
        language=user.language or "en",
        interests=[],
        travel_style="balanced",
    )


def load_profile_from_context(context: dict | None, user: User) -> ProfileResponse:
    base = build_default_profile(user)
    if not context:
        return base
    data = context.get(PROFILE_CONTEXT_KEY)
    if not data:
        return base
    stored = ProfileResponse.model_validate(data)
    stored_data = stored.model_dump(exclude_unset=False)
    stored_data["id"] = user.id
    stored_data["email"] = user.email
    return base.model_copy(update=stored_data)


async def persist_profile(
    repo: UserProfileRepository,
    *,
    user_id: uuid.UUID,
    profile: ProfileResponse,
    context: dict | None,
) -> None:
    snapshot = dict(context or {})
    snapshot.setdefault("user_context", build_default_context(user_id).model_dump(mode="json"))
    snapshot[PROFILE_CONTEXT_KEY] = profile.model_dump(by_alias=True, exclude_none=True)
    await repo.upsert_profile(user_id, snapshot)


@router.get("/profile", summary="Get Profile", response_model=ProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProfileResponse:
    repo = UserProfileRepository(db)
    stored = await repo.get_profile(current_user.id)
    if stored is None:
        profile = build_default_profile(current_user)
        await persist_profile(repo, user_id=current_user.id, profile=profile, context={})
        await db.commit()
        return profile
    return load_profile_from_context(stored.context, current_user)


@router.put("/profile", summary="Update Profile", response_model=ProfileResponse)
async def update_profile(
    payload: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProfileResponse:
    repo = UserProfileRepository(db)
    stored = await repo.get_profile(current_user.id)
    context = stored.context if stored else {}
    current = load_profile_from_context(context, current_user)
    update_data = payload.model_dump(exclude_unset=True)
    updated = current.model_copy(update=update_data)
    if payload.city:
        current_user.city = payload.city
    if payload.language:
        current_user.language = payload.language
    await persist_profile(repo, user_id=current_user.id, profile=updated, context=context)
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
