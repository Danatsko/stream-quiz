from typing import Annotated, Any

from fastapi import APIRouter, status, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_auth_context
from app.core.db import get_db_session
from app.core.limiter import limiter
from app.rooms.schemas import CreateRoomRequest, CreateRoomResponse
from app.rooms.service import create_room as service_create_room

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
