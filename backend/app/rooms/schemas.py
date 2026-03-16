from uuid import UUID
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
