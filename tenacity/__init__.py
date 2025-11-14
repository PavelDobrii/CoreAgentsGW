"""Minimal subset of :mod:`tenacity` used in tests."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Tuple, Type

__all__ = [
    "AsyncRetrying",
    "retry_if_exception_type",
    "stop_after_attempt",
    "wait_exponential",
]


@dataclass(slots=True)
class _StopAfterAttempt:
    max_attempt_number: int


def stop_after_attempt(attempt_number: int) -> _StopAfterAttempt:
    return _StopAfterAttempt(max_attempt_number=attempt_number)


def wait_exponential(**_: Any) -> None:  # pragma: no cover - placeholder
    return None


@dataclass(slots=True)
class retry_if_exception_type:  # noqa: N801 - mimic tenacity's naming
    exceptions: Tuple[Type[BaseException], ...]

    def __init__(self, *exceptions: Type[BaseException]):
        self.exceptions = exceptions or (Exception,)


class _AttemptContext:
    async def __aenter__(self) -> "_AttemptContext":  # pragma: no cover - trivial
        return self

    async def __aexit__(self, exc_type, exc, tb) -> bool:  # pragma: no cover - propagate
        return False


class AsyncRetrying:
    def __init__(self, *, stop: _StopAfterAttempt | None = None, **_: Any) -> None:
        self.max_attempts = (stop.max_attempt_number if stop else 1) or 1
        self._yielded = 0

    def __aiter__(self) -> "AsyncRetrying":
        self._yielded = 0
        return self

    async def __anext__(self) -> _AttemptContext:
        if self._yielded >= self.max_attempts:
            raise StopAsyncIteration
        self._yielded += 1
        return _AttemptContext()
