from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/healthz", summary="Health Check")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
