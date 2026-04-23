from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, status, Request, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_auth_context
from app.core.db import get_db_session
from app.core.limiter import limiter
from app.users.schemas import (
    GetMeResponse,
    GetMeSessionsResponse,
    GetMeSessionResponse,
    UpdateMeRequest,
)
from app.users.service import (
    get_me as service_get_me,
    update_me as service_update_me,
    get_me_sessions as service_get_me_sessions,
    get_me_session as service_get_me_session,
)

users_router = APIRouter()


@users_router.get(
    path="/me",
    status_code=status.HTTP_200_OK,
    response_model=GetMeResponse,
)
@limiter.limit("300/minute")
async def get_me(
    request: Request,
    auth_context: Annotated[dict[str, Any], Depends(get_current_auth_context)],
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
) -> GetMeResponse:
    user_uuid = auth_context["user_uuid"]
    result = await service_get_me(
        user_uuid=user_uuid,
        db_session=db_session,
    )

    return GetMeResponse(
        uuid=result["uuid"],
        username=result["username"],
        email=result["email"],
    )


@users_router.patch(
    path="/me",
    status_code=status.HTTP_204_NO_CONTENT,
)
@limiter.limit("300/minute")
async def update_me(
    request: Request,
    update_me_data: UpdateMeRequest,
    auth_context: Annotated[dict[str, Any], Depends(get_current_auth_context)],
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
) -> None:
    user_uuid = auth_context["user_uuid"]

    await service_update_me(
        user_uuid=user_uuid,
        update_me_data=update_me_data.model_dump(exclude_unset=True),
        db_session=db_session,
    )


@users_router.get(
    path="/me/sessions",
    status_code=status.HTTP_200_OK,
    response_model=GetMeSessionsResponse,
)
@limiter.limit("300/minute")
async def get_me_sessions(
    request: Request,
    auth_context: Annotated[dict[str, Any], Depends(get_current_auth_context)],
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=100)] = 10,
) -> GetMeSessionsResponse:
    user_uuid = auth_context["user_uuid"]
    result = await service_get_me_sessions(
        page=page,
        size=size,
        user_uuid=user_uuid,
        db_session=db_session,
    )

    return GetMeSessionsResponse(
        sessions=result["sessions"],
        total_sessions=result["total_sessions"],
        page=result["page"],
        size=result["size"],
        total_pages=result["total_pages"],
    )


@users_router.get(
    path="/me/sessions/{session_uuid}",
    status_code=status.HTTP_200_OK,
    response_model=GetMeSessionResponse,
)
@limiter.limit("300/minute")
async def get_me_session(
    request: Request,
    session_uuid: UUID,
    auth_context: Annotated[dict[str, Any], Depends(get_current_auth_context)],
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
) -> GetMeSessionResponse:
    user_uuid = auth_context["user_uuid"]
    result = await service_get_me_session(
        user_uuid=user_uuid,
        session_uuid=session_uuid,
        db_session=db_session,
    )

    return GetMeSessionResponse(
        uuid=result["uuid"],
        quiz_uuid=result["quiz_uuid"],
        title=result["title"],
        description=result["description"],
        time_seconds=result["time_seconds"],
        status=result["status"],
        questions=result["questions"],
        total_questions=result["total_questions"],
        total_score=result["total_score"],
        answers=result["answers"],
        total_answers=result["total_answers"],
        score=result["score"],
    )
