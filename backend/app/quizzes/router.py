from typing import Annotated, Any

from fastapi import APIRouter, status, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_auth_context
from app.core.db import get_db_session
from app.core.limiter import limiter
from app.quizzes.schemas import CreateQuizResponse, CreateQuizRequest
from app.quizzes.service import create_quiz as service_create_quiz

quizzes_router = APIRouter()


@quizzes_router.post(
    path="/",
    status_code=status.HTTP_201_CREATED,
    response_model=CreateQuizResponse,
)
@limiter.limit("300/minute")
async def create_quiz(
    request: Request,
    create_quiz_data: CreateQuizRequest,
    auth_context: Annotated[dict[str, Any], Depends(get_current_auth_context)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> CreateQuizResponse:
    user_uuid = auth_context["user_uuid"]
    result = await service_create_quiz(
        quiz_data=create_quiz_data.model_dump(),
        user_uuid=user_uuid,
        session=session,
    )

    return CreateQuizResponse(
        uuid=result["uuid"],
    )
