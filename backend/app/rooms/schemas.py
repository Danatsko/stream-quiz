from uuid import UUID
from datetime import datetime
from typing import Annotated

from pydantic import StringConstraints, field_validator

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


class GetRoomResponse(GetSummaryRoom):
    pass


class UpdateRoomRequest(Base):
    title: (
        Annotated[
            str,
            StringConstraints(
                min_length=3,
                max_length=100,
            ),
        ]
        | None
    ) = None
    description: (
        Annotated[
            str,
            StringConstraints(max_length=500),
        ]
        | None
    ) = None

    @field_validator("title", "description")
    @classmethod
    def prevent_explicit_null(cls, value):
        if value is None:
            raise ValueError("Null is not allowed for this field")

        return value
