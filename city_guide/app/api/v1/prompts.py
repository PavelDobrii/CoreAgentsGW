from __future__ import annotations

from fastapi import APIRouter

from ...schemas.prompts import RoutePromptsRequest
from ...schemas.responses import PromptsResponse

router = APIRouter(prefix="/v1", tags=["prompts"])


@router.post("/prompts/route", summary="Create Route Prompts", response_model=PromptsResponse)
async def build_route_prompts(payload: RoutePromptsRequest) -> PromptsResponse:
    base_prompt = f"User in {payload.user_context.city} seeking {payload.user_context.travel_style} trip"
    style_prompt = "Focus on cultural highlights and local cuisine."
    if payload.free_text:
        style_prompt += f" Additional notes: {payload.free_text}"
    return PromptsResponse(prompt_poi=base_prompt, prompt_style=style_prompt)
