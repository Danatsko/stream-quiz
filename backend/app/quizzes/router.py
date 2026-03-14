from uuid import UUID
from typing import Annotated, Any

from fastapi import APIRouter, status, Request, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_auth_context
from app.core.db import get_db_session
from app.core.limiter import limiter
from app.quizzes.schemas import (
    CreateQuizResponse,
    CreateQuizRequest,
    GetQuizzesResponse,
    GetQuizResponse,
    UpdateQuizRequest,
    FullUpdateQuizRequest,
)
from app.quizzes.service import (
    create_quiz as service_create_quiz,
    get_quizzes as service_get_quizzes,
    get_quiz as service_get_quiz,
    update_quiz as service_update_quiz,
    delete_quiz as service_delete_quiz,
    full_update_quiz as service_full_update_quiz,
)

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
        **create_quiz_data.model_dump(),
        user_uuid=user_uuid,
        session=session,
    )

    return CreateQuizResponse(uuid=result["uuid"])


@quizzes_router.get(
    path="/",
    status_code=status.HTTP_200_OK,
    response_model=GetQuizzesResponse,
)
@limiter.limit("300/minute")
async def get_quizzes(
    request: Request,
    auth_context: Annotated[dict[str, Any], Depends(get_current_auth_context)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=100)] = 10,
) -> GetQuizzesResponse:
    user_uuid = auth_context["user_uuid"]
    result = await service_get_quizzes(
        page=page,
        size=size,
        user_uuid=user_uuid,
        session=session,
    )

    return GetQuizzesResponse(
        quizzes=result["quizzes"],
        total_quizzes=result["total_quizzes"],
        page=result["page"],
        size=result["size"],
        total_pages=result["total_pages"],
    )


@quizzes_router.get(
    path="/{quiz_uuid}",
    status_code=status.HTTP_200_OK,
    response_model=GetQuizResponse,
)
@limiter.limit("300/minute")
async def get_quiz(
    request: Request,
    quiz_uuid: UUID,
    auth_context: Annotated[dict[str, Any], Depends(get_current_auth_context)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> GetQuizResponse:
    user_uuid = auth_context["user_uuid"]
    result = await service_get_quiz(
        quiz_uuid=quiz_uuid,
        user_uuid=user_uuid,
        session=session,
    )

    return GetQuizResponse(
        uuid=result["uuid"],
        creator_uuid=result["creator_uuid"],
        title=result["title"],
        description=result["description"],
        is_public=result["is_public"],
        questions=result["questions"],
        total_questions=result["total_questions"],
        created_at=result["created_at"],
    )


@quizzes_router.patch(
    path="/{quiz_uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
)
@limiter.limit("300/minute")
async def update_quiz(
    request: Request,
    quiz_uuid: UUID,
    update_quiz_data: UpdateQuizRequest,
    auth_context: Annotated[dict[str, Any], Depends(get_current_auth_context)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> None:
    user_uuid = auth_context["user_uuid"]

    await service_update_quiz(
        quiz_uuid=quiz_uuid,
        user_uuid=user_uuid,
        update_quiz_data=update_quiz_data.model_dump(exclude_unset=True),
        session=session,
    )


@quizzes_router.put(
    path="/{quiz_uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
)
@limiter.limit("300/minute")
async def full_update_quiz(
    request: Request,
    quiz_uuid: UUID,
    full_update_quiz_data: FullUpdateQuizRequest,
    auth_context: Annotated[dict[str, Any], Depends(get_current_auth_context)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> None:
    user_uuid = auth_context["user_uuid"]

    await service_full_update_quiz(
        quiz_uuid=quiz_uuid,
        user_uuid=user_uuid,
        full_update_quiz_data=full_update_quiz_data.model_dump(),
        session=session,
    )


@quizzes_router.delete(
    path="/{quiz_uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
)
@limiter.limit("300/minute")
async def delete_quiz(
    request: Request,
    quiz_uuid: UUID,
    auth_context: Annotated[dict[str, Any], Depends(get_current_auth_context)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> None:
    user_uuid = auth_context["user_uuid"]

    await service_delete_quiz(
        quiz_uuid=quiz_uuid,
        user_uuid=user_uuid,
        session=session,
    )
