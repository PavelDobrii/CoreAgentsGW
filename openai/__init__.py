"""Test stub for the OpenAI SDK.

The real ``openai`` package is not available in the execution environment.
Only a tiny subset is required for the unit tests — enough for the module to be
imported and for ``AsyncOpenAI`` to expose a ``responses.create`` coroutine.
"""

from __future__ import annotations

from typing import Any

__all__ = ["AsyncOpenAI"]


class _Responses:
    async def create(self, *args: Any, **kwargs: Any) -> Any:  # pragma: no cover - never called in tests
        raise RuntimeError("OpenAI SDK is not available in the test environment")


class AsyncOpenAI:  # pragma: no cover - helper used only for type compatibility
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.responses = _Responses()
