from typing import Annotated, Any
from uuid import UUID

from arq import ArqRedis
from fastapi import APIRouter, status, Request, Depends, Query
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_auth_context
from app.core.arq import get_arq_pool
from app.core.db import get_db_session
from app.core.limiter import limiter
from app.core.redis import get_redis_client
from app.rooms.schemas import (
    CreateRoomRequest,
    CreateRoomResponse,
    GetRoomsResponse,
    UpdateRoomRequest,
    GetRoomResponse,
    CreateSessionResponse,
    CreateSessionRequest,
    UpdateSessionRequest,
    GetSessionsResponse,
    GetSessionResponse,
)
from app.rooms.service import (
    create_room as service_create_room,
    get_rooms as service_get_rooms,
    get_room as service_get_room,
    update_room as service_update_room,
    delete_room as service_delete_room,
    create_session as service_create_session,
    get_sessions as service_get_sessions,
    get_session as service_get_session,
    update_session as service_update_session,
    delete_session as service_delete_session,
    start_session as service_start_session,
    stop_session as service_stop_session,
)

rooms_router = APIRouter()


@rooms_router.post(
    path="/",
    status_code=status.HTTP_201_CREATED,
    response_model=CreateRoomResponse,
)
@limiter.limit("300/minute")
async def create_room(
    request: Request,
    create_room_data: CreateRoomRequest,
    auth_context: Annotated[dict[str, Any], Depends(get_current_auth_context)],
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
) -> CreateRoomResponse:
    user_uuid = auth_context["user_uuid"]
    result = await service_create_room(
        title=create_room_data.title,
        description=create_room_data.description,
        user_uuid=user_uuid,
        db_session=db_session,
    )

    return CreateRoomResponse(uuid=result["uuid"])


@rooms_router.get(
    path="/",
    status_code=status.HTTP_200_OK,
    response_model=GetRoomsResponse,
)
@limiter.limit("300/minute")
async def get_rooms(
    request: Request,
    auth_context: Annotated[dict[str, Any], Depends(get_current_auth_context)],
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=100)] = 10,
) -> GetRoomsResponse:
    user_uuid = auth_context["user_uuid"]
    result = await service_get_rooms(
        page=page,
        size=size,
        user_uuid=user_uuid,
        db_session=db_session,
    )

    return GetRoomsResponse(
        rooms=result["rooms"],
        total_rooms=result["total_rooms"],
        page=result["page"],
        size=result["size"],
        total_pages=result["total_pages"],
    )


@rooms_router.get(
    path="/{room_uuid}",
    status_code=status.HTTP_200_OK,
    response_model=GetRoomResponse,
)
@limiter.limit("300/minute")
async def get_room(
    request: Request,
    room_uuid: UUID,
    auth_context: Annotated[dict[str, Any], Depends(get_current_auth_context)],
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
) -> GetRoomResponse:
    user_uuid = auth_context["user_uuid"]
    result = await service_get_room(
        room_uuid=room_uuid,
        user_uuid=user_uuid,
        db_session=db_session,
    )

    return GetRoomResponse(
        creator_uuid=result["creator_uuid"],
        uuid=result["uuid"],
        title=result["title"],
        description=result["description"],
        created_at=result["created_at"],
        updated_at=result["updated_at"],
    )


@rooms_router.patch(
    path="/{room_uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
)
@limiter.limit("300/minute")
async def update_room(
    request: Request,
    room_uuid: UUID,
    update_room_data: UpdateRoomRequest,
    auth_context: Annotated[dict[str, Any], Depends(get_current_auth_context)],
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
) -> None:
    user_uuid = auth_context["user_uuid"]

    await service_update_room(
        room_uuid=room_uuid,
        user_uuid=user_uuid,
        update_room_data=update_room_data.model_dump(exclude_unset=True),
        db_session=db_session,
    )


@rooms_router.delete(
    path="/{room_uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
)
@limiter.limit("300/minute")
async def delete_room(
    request: Request,
    room_uuid: UUID,
    auth_context: Annotated[dict[str, Any], Depends(get_current_auth_context)],
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
) -> None:
    user_uuid = auth_context["user_uuid"]

    await service_delete_room(
        room_uuid=room_uuid,
        user_uuid=user_uuid,
        db_session=db_session,
    )


@rooms_router.post(
    path="/{room_uuid}/sessions",
    status_code=status.HTTP_201_CREATED,
    response_model=CreateSessionResponse,
)
@limiter.limit("300/minute")
async def create_session(
    request: Request,
    room_uuid: UUID,
    create_session_data: CreateSessionRequest,
    auth_context: Annotated[dict[str, Any], Depends(get_current_auth_context)],
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
) -> CreateSessionResponse:
    user_uuid = auth_context["user_uuid"]
    result = await service_create_session(
        title=create_session_data.title,
        description=create_session_data.description,
        time_seconds=create_session_data.time_seconds,
        quiz_uuid=create_session_data.quiz_uuid,
        room_uuid=room_uuid,
        user_uuid=user_uuid,
        db_session=db_session,
    )

    return CreateSessionResponse(uuid=result["uuid"])


@rooms_router.get(
    path="/{room_uuid}/sessions",
    status_code=status.HTTP_200_OK,
    response_model=GetSessionsResponse,
)
@limiter.limit("300/minute")
async def get_sessions(
    request: Request,
    room_uuid: UUID,
    auth_context: Annotated[dict[str, Any], Depends(get_current_auth_context)],
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=100)] = 10,
) -> GetSessionsResponse:
    user_uuid = auth_context["user_uuid"]
    result = await service_get_sessions(
        page=page,
        size=size,
        room_uuid=room_uuid,
        user_uuid=user_uuid,
        db_session=db_session,
    )

    return GetSessionsResponse(
        sessions=result["sessions"],
        total_sessions=result["total_sessions"],
        page=page,
        size=size,
        total_pages=result["total_pages"],
    )


@rooms_router.get(
    path="/{room_uuid}/sessions/{session_uuid}",
    status_code=status.HTTP_200_OK,
    response_model=GetSessionResponse,
)
@limiter.limit("300/minute")
async def get_session(
    request: Request,
    room_uuid: UUID,
    session_uuid: UUID,
    auth_context: Annotated[dict[str, Any], Depends(get_current_auth_context)],
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    redis_client: Annotated[Redis, Depends(get_redis_client)],
) -> GetSessionResponse:
    user_uuid = auth_context["user_uuid"]
    result = await service_get_session(
        room_uuid=room_uuid,
        session_uuid=session_uuid,
        user_uuid=user_uuid,
        db_session=db_session,
        redis_client=redis_client,
    )

    return GetSessionResponse(
        uuid=result["uuid"],
        room_uuid=result["room_uuid"],
        quiz_uuid=result["quiz_uuid"],
        title=result["title"],
        description=result["description"],
        time_seconds=result["time_seconds"],
        status=result["status"],
        members=result["members"],
        total_members=result["total_members"],
        questions=result["questions"],
        total_questions=result["total_questions"],
        total_score=result["total_score"],
        created_at=result["created_at"],
        updated_at=result["updated_at"],
    )


@rooms_router.patch(
    path="/{room_uuid}/sessions/{session_uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
)
@limiter.limit("300/minute")
async def update_session(
    request: Request,
    room_uuid: UUID,
    session_uuid: UUID,
    update_session_data: UpdateSessionRequest,
    auth_context: Annotated[dict[str, Any], Depends(get_current_auth_context)],
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
) -> None:
    user_uuid = auth_context["user_uuid"]

    await service_update_session(
        room_uuid=room_uuid,
        session_uuid=session_uuid,
        user_uuid=user_uuid,
        update_session_data=update_session_data.model_dump(exclude_unset=True),
        db_session=db_session,
    )


@rooms_router.delete(
    path="/{room_uuid}/sessions/{session_uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
)
@limiter.limit("300/minute")
async def delete_session(
    request: Request,
    room_uuid: UUID,
    session_uuid: UUID,
    auth_context: Annotated[dict[str, Any], Depends(get_current_auth_context)],
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
) -> None:
    user_uuid = auth_context["user_uuid"]

    await service_delete_session(
        room_uuid=room_uuid,
        session_uuid=session_uuid,
        user_uuid=user_uuid,
        db_session=db_session,
    )


@rooms_router.post(
    path="/{room_uuid}/sessions/{session_uuid}/start",
    status_code=status.HTTP_204_NO_CONTENT,
)
@limiter.limit("300/minute")
async def start_session(
    request: Request,
    room_uuid: UUID,
    session_uuid: UUID,
    auth_context: Annotated[dict[str, Any], Depends(get_current_auth_context)],
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    redis_client: Annotated[Redis, Depends(get_redis_client)],
    arq_pool: Annotated[ArqRedis, Depends(get_arq_pool)],
) -> None:
    user_uuid = auth_context["user_uuid"]

    await service_start_session(
        room_uuid=room_uuid,
        session_uuid=session_uuid,
        user_uuid=user_uuid,
        db_session=db_session,
        redis_client=redis_client,
        arq_pool=arq_pool,
    )


@rooms_router.post(
    path="/{room_uuid}/sessions/{session_uuid}/stop",
    status_code=status.HTTP_204_NO_CONTENT,
)
@limiter.limit("300/minute")
async def stop_session(
    request: Request,
    room_uuid: UUID,
    session_uuid: UUID,
    auth_context: Annotated[dict[str, Any], Depends(get_current_auth_context)],
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    redis_client: Annotated[Redis, Depends(get_redis_client)],
) -> None:
    user_uuid = auth_context["user_uuid"]

    await service_stop_session(
        room_uuid=room_uuid,
        session_uuid=session_uuid,
        user_uuid=user_uuid,
        db_session=db_session,
        redis_client=redis_client,
    )
