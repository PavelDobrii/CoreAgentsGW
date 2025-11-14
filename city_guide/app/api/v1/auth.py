from __future__ import annotations

import uuid

from ...core import security
from ...db.repo import UserProfileRepository, UserRepository
from ...http import Application, HTTPException, Request, json_response
from .profile import build_default_profile, persist_profile


def _issue_tokens(user_id: uuid.UUID) -> tuple[str, str]:
    access = security.create_access_token(user_id)
    refresh = security.create_refresh_token(user_id)
    return access, refresh


def register_routes(app: Application) -> None:
    user_repo = UserRepository()
    profile_repo = UserProfileRepository()

    @app.route("POST", "/v1/register", summary="Register")
    def register(request: Request):
        payload = request.json or {}
        email = (payload.get("email") or "").strip().lower()
        password = payload.get("password")
        if not email or not password:
            raise HTTPException(400, "Email and password are required")
        if user_repo.get_by_email(email):
            raise HTTPException(400, "Email already registered")
        user = user_repo.create_user(
            email=email,
            password_hash=security.hash_password(password),
            first_name=payload.get("firstName"),
            last_name=payload.get("lastName"),
            phone=payload.get("phoneNumber"),
            country=payload.get("country"),
            city=payload.get("city"),
        )
        profile = build_default_profile(user)
        persist_profile(profile_repo, user.id, profile)
        access, refresh = _issue_tokens(user.id)
        return json_response({"access_token": access, "refresh_token": refresh, "user": profile}, status_code=201)

    @app.route("POST", "/v1/login", summary="Login")
    def login(request: Request):
        payload = request.json or {}
        email = (payload.get("email") or "").strip().lower()
        password = payload.get("password") or ""
        user = user_repo.get_by_email(email)
        if user is None or not security.verify_password(password, user.password_hash):
            raise HTTPException(401, "Invalid credentials")
        stored = profile_repo.get_profile(user.id)
        profile = build_default_profile(user)
        if stored:
            profile = profile | stored.context.get("profile", {})
            profile["id"] = str(user.id)
            profile["email"] = user.email
        access, refresh = _issue_tokens(user.id)
        return json_response({"access_token": access, "refresh_token": refresh, "user": profile})

    @app.route("POST", "/v1/refresh", summary="Refresh Token")
    def refresh(request: Request):
        payload = request.json or {}
        token = payload.get("refreshToken")
        if not token:
            raise HTTPException(400, "refreshToken is required")
        try:
            decoded = security.decode_refresh_token(token)
        except security.InvalidToken as exc:  # pragma: no cover
            raise HTTPException(401, "Invalid refresh token") from exc
        user_id = uuid.UUID(decoded["sub"])
        user = user_repo.get_by_id(user_id)
        if user is None or not user.is_active:
            raise HTTPException(401, "Inactive user")
        access, refresh_token = _issue_tokens(user.id)
        return json_response({"access_token": access, "refresh_token": refresh_token})
