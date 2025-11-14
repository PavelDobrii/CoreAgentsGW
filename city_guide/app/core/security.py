from __future__ import annotations

import hashlib
import uuid
from typing import Any


class InvalidToken(Exception):
    """Raised when a token cannot be validated."""


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not hashed_password:
        return False
    return hash_password(plain_password) == hashed_password


_access_tokens: dict[str, uuid.UUID] = {}
_refresh_tokens: dict[str, uuid.UUID] = {}


def reset_tokens() -> None:
    _access_tokens.clear()
    _refresh_tokens.clear()


def _store_token(store: dict[str, uuid.UUID], subject: uuid.UUID) -> str:
    token = uuid.uuid4().hex
    store[token] = subject
    return token


def create_access_token(subject: uuid.UUID) -> str:
    return _store_token(_access_tokens, subject)


def create_refresh_token(subject: uuid.UUID) -> str:
    return _store_token(_refresh_tokens, subject)


def _decode_token(token: str, store: dict[str, uuid.UUID]) -> dict[str, Any]:
    user_id = store.get(token)
    if user_id is None:
        raise InvalidToken
    return {"sub": str(user_id)}


def decode_access_token(token: str) -> dict[str, Any]:
    return _decode_token(token, _access_tokens)


def decode_refresh_token(token: str) -> dict[str, Any]:
    return _decode_token(token, _refresh_tokens)
