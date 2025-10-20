from __future__ import annotations

from pydantic import BaseModel

from .route import RouteDraftResponse, Suggestion


class PromptsResponse(BaseModel):
    prompt_poi: str
    prompt_style: str


class SuggestionsResponse(BaseModel):
    suggestions: list[Suggestion]


class RouteDraftsResponse(BaseModel):
    route: RouteDraftResponse
