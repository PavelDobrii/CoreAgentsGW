from __future__ import annotations

import uuid
from collections.abc import AsyncIterator

from fastapi import Depends, HTTPException, Request, status
from fastapi.security.utils import get_authorization_scheme_param
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from .config import settings
from . import security
from ..db.models import User
from ..db.repo import UserRepository

engine = create_async_engine(settings.async_database_url, echo=settings.echo_sql)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)


async def get_db() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session


def override_engine(url: str) -> None:
    global engine, SessionLocal
    engine = create_async_engine(url, echo=settings.echo_sql)
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> User:
    auth_header = request.headers.get("Authorization")
    scheme, token = get_authorization_scheme_param(auth_header)
    if not token or scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    try:
        payload = security.decode_access_token(token)
    except security.InvalidToken as exc:  # noqa: PERF203
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token") from exc

    user_id = payload.get("sub")
    try:
        user_uuid = uuid.UUID(str(user_id))
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token") from exc

    repo = UserRepository(db)
    user = await repo.get_by_id(user_uuid)
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return user
