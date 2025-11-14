from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...core import security
from ...core.deps import get_db
from ...db.models import User
from ...db.repo import UserProfileRepository, UserRepository
from ...schemas.auth import AuthResponse, LoginData, RefreshRequest, RegisterData, Tokens
from ...schemas.profile import ProfileResponse
from . import profile as profile_module

router = APIRouter(prefix="/v1", tags=["auth"])
compat_router = APIRouter(prefix="", tags=["auth"], include_in_schema=False)


async def _ensure_profile(repo: UserProfileRepository, user: User) -> ProfileResponse:
    stored = await repo.get_profile(user.id)
    if stored is None:
        profile = profile_module.build_default_profile(user)
        await profile_module.persist_profile(repo, user_id=user.id, profile=profile, context={})
        return profile
    return profile_module.load_profile_from_context(stored.context, user)


def _issue_tokens(user_id: uuid.UUID) -> tuple[str, str]:
    access = security.create_access_token(user_id)
    refresh = security.create_refresh_token(user_id)
    return access, refresh


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterData, db: AsyncSession = Depends(get_db)) -> AuthResponse:
    user_repo = UserRepository(db)
    existing = await user_repo.get_by_email(payload.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    password_hash = security.hash_password(payload.password)
    user = await user_repo.create_user(
        email=payload.email,
        password_hash=password_hash,
        first_name=payload.first_name,
        last_name=payload.last_name,
        phone=payload.phone_number,
        country=payload.country,
        city=payload.city,
    )
    profile_repo = UserProfileRepository(db)
    profile = await _ensure_profile(profile_repo, user)
    await db.commit()

    access_token, refresh_token = _issue_tokens(user.id)
    return AuthResponse(access_token=access_token, refresh_token=refresh_token, user=profile)


@router.post("/login", response_model=AuthResponse)
async def login(payload: LoginData, db: AsyncSession = Depends(get_db)) -> AuthResponse:
    user_repo = UserRepository(db)
    user = await user_repo.get_by_email(payload.email)
    if user is None or not security.verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    profile_repo = UserProfileRepository(db)
    profile = await _ensure_profile(profile_repo, user)
    await db.commit()

    access_token, refresh_token = _issue_tokens(user.id)
    return AuthResponse(access_token=access_token, refresh_token=refresh_token, user=profile)


async def _refresh_tokens(payload: RefreshRequest, db: AsyncSession) -> Tokens:
    try:
        decoded = security.decode_refresh_token(payload.refresh_token)
    except security.InvalidToken as exc:  # noqa: PERF203
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token") from exc

    user_id = decoded.get("sub")
    try:
        user_uuid = uuid.UUID(str(user_id))
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token") from exc

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_uuid)
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user")

    access_token, refresh_token = _issue_tokens(user.id)
    return Tokens(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=Tokens)
async def refresh(payload: RefreshRequest, db: AsyncSession = Depends(get_db)) -> Tokens:
    return await _refresh_tokens(payload, db)


@compat_router.post("/refresh", response_model=Tokens)
async def refresh_without_prefix(payload: RefreshRequest, db: AsyncSession = Depends(get_db)) -> Tokens:
    """Compatibility shim for the frontend's absolute `/refresh` call."""

    return await _refresh_tokens(payload, db)
