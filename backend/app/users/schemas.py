from uuid import UUID
from typing import Annotated

from pydantic import StringConstraints, EmailStr, Field, field_validator

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


class SessionQuestionOptionBase(Base):
    uuid: UUID
    text: Annotated[
        str,
        StringConstraints(
            min_length=3,
            max_length=500,
        ),
    ]


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


class SessionMemberAnswerSelectedOptionBase(Base):
    uuid: UUID
    is_correct: bool


class SessionMemberAnswerBase(Base):
    question_uuid: UUID
    selected_options: list[SessionMemberAnswerSelectedOptionBase]
    score: float


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


class UpdateMeRequest(Base):
    username: (
        Annotated[
            str,
            StringConstraints(
                min_length=3,
                max_length=30,
            ),
        ]
        | None
    ) = None

    @field_validator("username")
    @classmethod
    def prevent_explicit_null(cls, value):
        if value is None:
            raise ValueError("Null is not allowed for this field")

        return value


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


class GetMeSessionResponse(SummarySession):
    questions: list[SessionQuestionBase]
    total_questions: int
    total_score: float
    answers: list[SessionMemberAnswerBase]
    total_answers: int
    score: float
