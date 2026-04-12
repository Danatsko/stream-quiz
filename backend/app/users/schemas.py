from uuid import UUID
from typing import Annotated

from pydantic import StringConstraints, EmailStr, Field

from app.core.schemas import Base


class UserBase(Base):
    uuid: UUID
    username: Annotated[
        str,
        StringConstraints(
            min_length=3,
            max_length=30,
        ),
    ]
    email: EmailStr


class SessionBase(Base):
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
    time_seconds: Annotated[
        int,
        Field(
            gt=0,
            le=604800,
        ),
    ]


class GetMeResponse(UserBase):
    pass


class SummarySession(SessionBase):
    uuid: UUID
    quiz_uuid: UUID | None
    status: str


class GetMeSessionsResponse(Base):
    sessions: list[SummarySession]
    total_sessions: int
    page: int
    size: int
    total_pages: int
