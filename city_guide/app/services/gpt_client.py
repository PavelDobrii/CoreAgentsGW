from __future__ import annotations

import json
import logging
from typing import Sequence

from openai import AsyncOpenAI
from tenacity import AsyncRetrying, retry_if_exception_type, stop_after_attempt, wait_exponential

from ..core.config import settings

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


def get_gpt_client() -> GPTClient:
    return GPTClient()
