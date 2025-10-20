from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


async def synthesize(text: str, *, language: str = "en-US") -> bytes:
    logger.info("Google TTS not yet implemented, returning empty payload")
    return b""
