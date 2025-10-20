from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.repo import UserProfileRepository
from ...schemas.quiz import QuizRequest, QuizResponse
from ...core.deps import get_db

router = APIRouter(prefix="/v1", tags=["quiz"])


@router.post("/quiz", summary="Submit Quiz", response_model=QuizResponse)
async def submit_quiz(payload: QuizRequest, db: AsyncSession = Depends(get_db)) -> QuizResponse:
    repo = UserProfileRepository(db)
    context = {
        "answers": [answer.model_dump() for answer in payload.answers],
    }
    if payload.user_context is not None:
        context["user_context"] = payload.user_context.model_dump()
    await repo.upsert_profile(payload.user_id, context)
    await db.commit()
    return QuizResponse(user_id=payload.user_id)
