from __future__ import annotations

import uuid

from ..db.repo import UserProfileRepository

DEFAULT_CONTEXT = {
    "city": "Vilnius",
    "language": "en",
    "travel_style": "balanced",
    "interests": [],
    "transport_mode": "walking",
    "duration_min": 180,
}


def build_default_context(user_id: uuid.UUID) -> dict:
    context = dict(DEFAULT_CONTEXT)
    context["user_id"] = str(user_id)
    return context


def get_profile_or_default(user_id: uuid.UUID) -> dict:
    repo = UserProfileRepository()
    profile = repo.get_profile(user_id)
    if profile is None:
        return build_default_context(user_id)
    stored = profile.context or {}
    return build_default_context(user_id) | stored.get("user_context", {})
