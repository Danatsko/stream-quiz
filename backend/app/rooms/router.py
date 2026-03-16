from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, status, Request, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_auth_context
from app.core.db import get_db_session
from app.core.limiter import limiter
from app.rooms.schemas import (
    CreateRoomRequest,
    CreateRoomResponse,
    GetRoomsResponse,
    UpdateRoomRequest,
)
from app.rooms.service import (
    create_room as service_create_room,
    get_rooms as service_get_rooms,
    update_room as service_update_room,
    delete_room as service_delete_room,
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
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> CreateRoomResponse:
    user_uuid = auth_context["user_uuid"]
    result = await service_create_room(
        **create_room_data.model_dump(),
        user_uuid=user_uuid,
        session=session,
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
    session: Annotated[AsyncSession, Depends(get_db_session)],
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=100)] = 10,
) -> GetRoomsResponse:
    user_uuid = auth_context["user_uuid"]
    result = await service_get_rooms(
        page=page,
        size=size,
        user_uuid=user_uuid,
        session=session,
    )

    return GetRoomsResponse(
        rooms=result["rooms"],
        total_rooms=result["total_rooms"],
        page=result["page"],
        size=result["size"],
        total_pages=result["total_pages"],
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
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> None:
    user_uuid = auth_context["user_uuid"]

    await service_update_room(
        room_uuid=room_uuid,
        user_uuid=user_uuid,
        update_room_data=update_room_data.model_dump(exclude_unset=True),
        session=session,
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
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> None:
    user_uuid = auth_context["user_uuid"]

    await service_delete_room(
        room_uuid=room_uuid,
        user_uuid=user_uuid,
        session=session,
    )
