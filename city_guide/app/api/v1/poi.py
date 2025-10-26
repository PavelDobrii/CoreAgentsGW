from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.deps import get_db
from ...db.repo import RouteDraftRepository
from ...schemas.responses import SuggestionsResponse
from ...schemas.route import Suggestion
from .routes import _parse_uuid

router = APIRouter(prefix="/v1", tags=["poi"])


@router.get("/poi/suggest", summary="Suggest POIs", response_model=SuggestionsResponse)
async def suggest_poi(
    route_id: uuid.UUID = Query(..., description="Route identifier"),
    db: AsyncSession = Depends(get_db),
) -> SuggestionsResponse:
    """Возвращает подборку дополнительных точек интереса для маршрута."""
    repo = RouteDraftRepository(db)
    draft = await repo.get_draft(route_id)
    if draft is None:
        raise HTTPException(status_code=404, detail="Route not found")
    items: list[Suggestion] = []
    for point in draft.points[:3]:
        items.append(
            Suggestion(
                poi_id=_parse_uuid(point.poi_id),
                distance_m=200,
                reason=f"Close to {point.name}",
            )
        )
    return SuggestionsResponse(suggestions=items)
