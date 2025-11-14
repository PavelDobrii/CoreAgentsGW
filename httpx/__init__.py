"""Minimal stub of :mod:`httpx` for offline tests."""

from __future__ import annotations

from typing import Any

__all__ = ["AsyncClient", "HTTPError"]


class HTTPError(Exception):
    """Placeholder exception matching the real library's name."""


class _Response:
    def __init__(self, payload: dict[str, Any] | None = None) -> None:
        self._payload = payload or {}

    def json(self) -> dict[str, Any]:  # pragma: no cover - unused helper
        return self._payload

    def raise_for_status(self) -> None:  # pragma: no cover - placeholder
        return None


class AsyncClient:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._response = _Response()

    async def __aenter__(self) -> "AsyncClient":  # pragma: no cover - trivial
        return self

    async def __aexit__(self, exc_type, exc, tb) -> bool:  # pragma: no cover - propagate
        return False

    async def get(self, *args: Any, **kwargs: Any) -> _Response:  # pragma: no cover - fallback
        raise HTTPError("HTTP requests are not supported in the test environment")
