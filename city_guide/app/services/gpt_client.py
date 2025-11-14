from __future__ import annotations

import json
import logging
from typing import Any, Sequence

from openai import AsyncOpenAI
from tenacity import AsyncRetrying, retry_if_exception_type, stop_after_attempt, wait_exponential

from ..core.config import settings
from ..schemas.poi import (
    BrainstormPOIRequest,
    BrainstormPOIResponse,
    BrainstormedPOI,
)

logger = logging.getLogger(__name__)


class GPTClient:
    def __init__(self) -> None:
        if settings.openai_api_key:
            self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        else:
            self.client = None
        self.model = settings.gpt_model

    async def _completion(self, messages: list[dict[str, str]], response_format: dict | None = None) -> dict:
        if not self.client:
            raise RuntimeError("OpenAI client not configured")
        async for attempt in AsyncRetrying(
            wait=wait_exponential(multiplier=1, max=10),
            stop=stop_after_attempt(3),
            retry=retry_if_exception_type(Exception),
            reraise=True,
        ):
            with attempt:
                response = await self.client.responses.create(
                    model=self.model,
                    input=messages,
                    response_format=response_format or {"type": "json_object"},
                    temperature=0.2,
                )
                return json.loads(response.output[0].content[0].text)
        raise RuntimeError("Failed to obtain completion")

    async def select_poi(self, user_ctx: dict, candidates: Sequence[dict], k: int) -> list[str]:
        if not candidates:
            return []
        if not self.client:
            logger.info("OpenAI not configured, falling back to rating selection")
            sorted_candidates = sorted(candidates, key=lambda c: c.get("rating", 0), reverse=True)
            return [c["poi_id"] for c in sorted_candidates[:k]]
        payload = {
            "user": user_ctx,
            "candidates": candidates,
            "limit": k,
        }
        try:
            data = await self._completion(
                messages=[{"role": "user", "content": json.dumps(payload)}],
                response_format={"type": "json_object"},
            )
            ids = data.get("poi_ids") or []
            return [str(i) for i in ids][:k]
        except Exception as exc:  # noqa: BLE001
            logger.exception("GPT selection failed, using fallback: %s", exc)
            sorted_candidates = sorted(candidates, key=lambda c: c.get("rating", 0), reverse=True)
            return [c["poi_id"] for c in sorted_candidates[:k]]

    async def order_route(self, user_ctx: dict, nodes: Sequence[dict], matrix: Sequence[Sequence[float]]) -> list[str]:
        if not nodes:
            return []
        if not self.client:
            logger.info("OpenAI not configured, falling back to sequential order")
            return [node["poi_id"] for node in nodes]
        payload = {
            "user": user_ctx,
            "nodes": nodes,
            "distance_matrix": matrix,
        }
        try:
            data = await self._completion(
                messages=[{"role": "user", "content": json.dumps(payload)}],
                response_format={"type": "json_object"},
            )
            ids = data.get("poi_order") or []
            order = [str(i) for i in ids]
            if len(order) != len(nodes):
                raise ValueError("Invalid response length")
            return order
        except Exception as exc:  # noqa: BLE001
            logger.exception("GPT ordering failed, using fallback: %s", exc)
            return [node["poi_id"] for node in nodes]

    async def brainstorm_poi(self, req: BrainstormPOIRequest) -> BrainstormPOIResponse:
        if not self.client:
            logger.info("OpenAI not configured, skipping POI brainstorming")
            logger.info("Brainstormed %d POIs", 0)
            return BrainstormPOIResponse(items=[])

        prompt_sections: list[str] = [
            "You are an expert travel planner. Brainstorm interesting points of interest for the traveler.",
        ]

        locality_parts: list[str] = []
        if req.locality_id:
            locality_parts.append(f"Locality ID: {req.locality_id}.")
        if req.start_location:
            locality_parts.append(
                "Start location coordinates: "
                f"lat={req.start_location.lat}, lng={req.start_location.lng}."
            )
        if locality_parts:
            prompt_sections.append("Location context: " + " ".join(locality_parts))

        if req.user_context:
            prompt_sections.append(
                "Traveler profile and interests: "
                + json.dumps(req.user_context, ensure_ascii=False)
            )

        if req.route_options:
            prompt_sections.append(
                "Route preferences and constraints: "
                + json.dumps(req.route_options, ensure_ascii=False)
            )

        prompt_sections.append(
            "Return diverse POIs with human-friendly names, short descriptions, and priority scores."
        )

        prompt = "\n".join(prompt_sections)
        logger.debug("Brainstorm POI prompt: %s", prompt)

        response_format: dict[str, Any] = {
            "type": "json_schema",
            "json_schema": {
                "name": "brainstorm_poi_response",
                "schema": {
                    "type": "object",
                    "properties": {
                        "items": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string"},
                                    "city": {"type": ["string", "null"]},
                                    "country": {"type": ["string", "null"]},
                                    "category": {"type": ["string", "null"]},
                                    "description": {"type": ["string", "null"]},
                                    "priority": {"type": ["number", "null"]},
                                },
                                "required": ["title"],
                            },
                        }
                    },
                    "required": ["items"],
                },
                "strict": True,
            },
        }

        try:
            data = await self._completion(
                messages=[{"role": "user", "content": prompt}],
                response_format=response_format,
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("GPT brainstorming failed: %s", exc)
            logger.info("Brainstormed %d POIs", 0)
            return BrainstormPOIResponse(items=[])

        raw_items = data.get("items") or []
        pois = [BrainstormedPOI.model_validate(item) for item in raw_items]

        logger.info("Brainstormed %d POIs", len(pois))

        return BrainstormPOIResponse(items=pois)


def get_gpt_client() -> GPTClient:
    return GPTClient()
