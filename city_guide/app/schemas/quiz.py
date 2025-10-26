from __future__ import annotations

import uuid
from typing import Literal, TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from .route import UserRouteContext


class QuizAnswer(BaseModel):
    question_id: str = Field(..., min_length=1)
    answer: str = Field(..., min_length=1)


class QuizRequest(BaseModel):
    user_id: uuid.UUID
    answers: list[QuizAnswer]
    user_context: UserRouteContext | None = None


class QuizResponse(BaseModel):
    user_id: uuid.UUID
    acknowledged: bool = True


from .route import UserRouteContext

QuizRequest.model_rebuild()
