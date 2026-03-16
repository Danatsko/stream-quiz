from uuid import UUID
from datetime import datetime
from typing import Annotated

from pydantic import StringConstraints

from app.core.schemas import Base


class RoomBase(Base):
    title: Annotated[
        str,
        StringConstraints(
            min_length=3,
            max_length=100,
        ),
    ]
    description: Annotated[
        str,
        StringConstraints(max_length=500),
    ]


class CreateRoomRequest(RoomBase):
    pass


class CreateRoomResponse(Base):
    uuid: UUID


class GetSummaryRoom(RoomBase):
    creator_uuid: UUID
    uuid: UUID
    created_at: datetime
    updated_at: datetime


class GetRoomsResponse(Base):
    rooms: list[GetSummaryRoom]
    total_rooms: int
    page: int
    size: int
    total_pages: int
