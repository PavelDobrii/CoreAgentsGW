from __future__ import annotations

import uuid

from ...api.dependencies import build_default_context
from ...core import deps, security
from ...db.repo import UserProfileRepository, UserRepository
from ...http import Application, HTTPException, Request, json_response

PROFILE_KEY = "profile"


def build_default_profile(user) -> dict:
    return {
        "id": str(user.id),
        "email": user.email,
        "firstName": user.first_name or "",
        "lastName": user.last_name or "",
        "phone": user.phone or "",
        "country": user.country or "",
        "city": user.city or "",
        "isActive": user.is_active,
        "language": user.language or "en",
        "gender": None,
        "age": None,
        "region": None,
        "interests": [],
        "travelStyle": "balanced",
    }


def load_profile_from_context(context: dict | None, user) -> dict:
    base = build_default_profile(user)
    if not context:
        return base
    stored = context.get(PROFILE_KEY)
    if not stored:
        return base
    merged = dict(base)
    merged.update(stored)
    merged["id"] = str(user.id)
    merged["email"] = user.email
    return merged


def persist_profile(repo: UserProfileRepository, user_id: uuid.UUID, profile: dict) -> None:
    current = repo.get_profile(user_id)
    snapshot = dict(current.context if current else {})
    snapshot.setdefault("user_context", build_default_context(user_id))
    snapshot[PROFILE_KEY] = profile
    repo.upsert_profile(user_id, snapshot)


def register_routes(app: Application) -> None:
    profile_repo = UserProfileRepository()
    user_repo = UserRepository()

    def _ensure_user(request: Request):
        authorization = request.headers.get("Authorization")
        return deps.get_current_user(authorization)

    @app.route("GET", "/v1/profile", summary="Get Profile")
    def get_profile(request: Request):
        user = _ensure_user(request)
        stored = profile_repo.get_profile(user.id)
        if stored is None:
            profile = build_default_profile(user)
            persist_profile(profile_repo, user.id, profile)
            return json_response(profile)
        return json_response(load_profile_from_context(stored.context, user))

    @app.route("PUT", "/v1/profile", summary="Update Profile")
    def update_profile(request: Request):
        user = _ensure_user(request)
        payload = request.json or {}
        stored = profile_repo.get_profile(user.id)
        context = stored.context if stored else {}
        current = load_profile_from_context(context, user)
        updated = dict(current)
        updated.update({k: v for k, v in payload.items() if v is not None})
        if payload.get("city"):
            user.city = payload["city"]
        if payload.get("language"):
            user.language = payload["language"]
        persist_profile(profile_repo, user.id, updated)
        user_repo.save_user(user)
        return json_response(updated)

    @app.route("GET", "/v1/profile/context", summary="Get Profile Context")
    def get_profile_context(request: Request):
        user_id = request.params.get("user_id")
        if not user_id:
            raise HTTPException(400, "user_id is required")
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError as exc:  # pragma: no cover
            raise HTTPException(400, "Invalid user_id") from exc
        stored = profile_repo.get_profile(user_uuid)
        if stored is None:
            return json_response(build_default_context(user_uuid))
        context = stored.context.get("user_context", {})
        return json_response(build_default_context(user_uuid) | context)

    @app.route("POST", "/v1/profile/context", summary="Create Profile Context", include_in_schema=True)
    def create_profile_context(request: Request):
        payload = request.json or {}
        try:
            user_uuid = uuid.UUID(str(payload["user_id"]))
        except (KeyError, ValueError) as exc:
            raise HTTPException(400, "user_id is required") from exc
        base = build_default_context(user_uuid)
        base.update({k: v for k, v in payload.items() if k in base})
        stored = profile_repo.get_profile(user_uuid)
        context = stored.context if stored else {}
        context = dict(context)
        context["user_context"] = base
        profile_repo.upsert_profile(user_uuid, context)
        return json_response(base, status_code=201)
