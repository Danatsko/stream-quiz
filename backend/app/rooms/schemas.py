from uuid import UUID
from datetime import datetime
from typing import Annotated

from pydantic import StringConstraints, field_validator, Field

from app.core.schemas import Base


class RoomBase(Base):
    title: Annotated[
        str,
        StringConstraints(
            min_length=1,
            max_length=100,
        ),
    ]
    description: Annotated[
        str,
        StringConstraints(max_length=500),
    ]


class SessionQuestionOptionBase(Base):
    uuid: UUID
    text: Annotated[
        str,
        StringConstraints(
            min_length=1,
            max_length=500,
        ),
    ]
    is_correct: bool


class SessionQuestionBase(Base):
    uuid: UUID
    text: Annotated[
        str,
        StringConstraints(
            min_length=3,
            max_length=500,
        ),
    ]
    is_multiple_answers: bool
    options: list[SessionQuestionOptionBase]


class SessionMemberAnswerBase(Base):
    question_uuid: UUID
    selected_option_uuids: list[UUID]
    score: float


class SessionMemberBase(Base):
    user_uuid: UUID | None
    username: Annotated[
        str,
        StringConstraints(
            min_length=3,
            max_length=30,
        ),
    ]
    answers: list[SessionMemberAnswerBase]
    total_answers: int
    score: float


class SessionBase(Base):
    title: Annotated[
        str,
        StringConstraints(
            min_length=1,
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


class CreateRoomRequest(RoomBase):
    pass


class CreateRoomResponse(Base):
    uuid: UUID


class SummaryRoom(RoomBase):
    creator_uuid: UUID
    uuid: UUID
    created_at: datetime
    updated_at: datetime


class GetRoomsResponse(Base):
    rooms: list[SummaryRoom]
    total_rooms: int
    page: int
    size: int
    total_pages: int


class GetRoomResponse(SummaryRoom):
    pass


class UpdateRoomRequest(Base):
    title: (
        Annotated[
            str,
            StringConstraints(
                min_length=1,
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


class CreateSessionRequest(SessionBase):
    quiz_uuid: UUID


class CreateSessionResponse(Base):
    uuid: UUID


class SummarySession(SessionBase):
    uuid: UUID
    room_uuid: UUID
    quiz_uuid: UUID | None
    status: str
    created_at: datetime
    updated_at: datetime


class GetSessionsResponse(Base):
    sessions: list[SummarySession]
    total_sessions: int
    page: int
    size: int
    total_pages: int


class GetSessionResponse(SummarySession):
    members: list[SessionMemberBase]
    total_members: int
    questions: list[SessionQuestionBase]
    total_questions: int
    total_score: float


class UpdateSessionRequest(Base):
    quiz_uuid: UUID | None = None
    title: (
        Annotated[
            str,
            StringConstraints(
                min_length=1,
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
    time_seconds: (
        Annotated[
            int,
            Field(
                gt=0,
                le=604800,
            ),
        ]
        | None
    ) = None

    @field_validator("quiz_uuid", "title", "description", "time_seconds")
    @classmethod
    def prevent_explicit_null(cls, value):
        if value is None:
            raise ValueError("Null is not allowed for this field")

        return value
