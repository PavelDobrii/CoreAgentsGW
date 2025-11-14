from __future__ import annotations

import os
import uuid

from ..db import database
from ..db.repo import UserRepository
from . import security
from .config import settings


def reset_state() -> None:
    security.reset_tokens()
    if settings.testing or os.getenv("PYTEST_CURRENT_TEST"):
        database.reset()


def get_db():  # compatibility shim
    return UserRepository()


def override_engine(_: str) -> None:  # pragma: no cover - kept for API compatibility
    reset_state()


def _extract_token(header: str | None) -> str:
    if not header:
        raise security.InvalidToken
    parts = header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise security.InvalidToken
    return parts[1]


def get_current_user(authorization: str | None):
    token = _extract_token(authorization)
    payload = security.decode_access_token(token)
    user_id = uuid.UUID(payload["sub"])
    repo = UserRepository()
    user = repo.get_by_id(user_id)
    if user is None or not user.is_active:
        raise security.InvalidToken
    return user
