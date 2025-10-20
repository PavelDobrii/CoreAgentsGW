from __future__ import annotations

from pydantic import BaseModel

from .route import UserRouteContext


class RoutePromptsRequest(BaseModel):
    user_context: UserRouteContext
    free_text: str | None = None
