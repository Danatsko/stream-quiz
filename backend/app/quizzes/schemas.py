import uuid
from typing import Annotated, Self

from pydantic import StringConstraints, Field, model_validator, field_validator

from app.core.schemas import Base


class QuizQuestionOptionBase(Base):
    text: Annotated[
        str,
        StringConstraints(
            min_length=3,
            max_length=500,
        ),
    ]


class QuizQuestionBase(Base):
    text: Annotated[
        str,
        StringConstraints(
            min_length=3,
            max_length=500,
        ),
    ]
    is_multiple_answers: bool


class QuizBase(Base):
    title: Annotated[
        str,
        StringConstraints(
            min_length=3,
            max_length=100,
        ),
    ]
    description: Annotated[
        str,
        StringConstraints(
            min_length=3,
            max_length=500,
        ),
    ]
    is_public: bool


class CreateQuizQuestionOption(QuizQuestionOptionBase):
    is_correct: bool


class CreateQuizQuestion(QuizQuestionBase):
    options: list[CreateQuizQuestionOption] = Field(min_length=1)

    @model_validator(mode="after")
    def check_answer_logic(self) -> Self:
        correct_count = sum(1 for option in self.options if option.is_correct)

        if correct_count == 0:
            raise ValueError("The question must have at least one correct option")

        if not self.is_multiple_answers and correct_count > 1:
            raise ValueError(
                "Single-choice questions must have exactly one correct option"
            )

        return self


class CreateQuiz(QuizBase):
    questions: list[CreateQuizQuestion] = Field(min_length=1)


class CreateQuizRequest(Base):
    title: Annotated[
        str,
        StringConstraints(
            min_length=3,
            max_length=100,
        ),
    ]
    description: Annotated[
        str,
        StringConstraints(
            min_length=3,
            max_length=500,
        ),
    ]


class CreateQuizResponse(Base):
    uuid: uuid.UUID


class GetSummaryQuiz(QuizBase):
    creator_uuid: uuid.UUID | None
    uuid: uuid.UUID
    total_questions: int


class GetQuizzesResponse(Base):
    quizzes: list[GetSummaryQuiz]
    total_quizzes: int
    page: int
    size: int
    total_pages: int


class GetDetailedQuizQuestionOption(QuizQuestionOptionBase):
    uuid: uuid.UUID
    is_correct: bool | None


class GetDetailedQuizQuestion(QuizQuestionBase):
    uuid: uuid.UUID
    options: list[GetDetailedQuizQuestionOption]


class GetDetailedQuiz(QuizBase):
    creator_uuid: uuid.UUID | None
    uuid: uuid.UUID
    questions: list[GetDetailedQuizQuestion]


class GetQuizResponse(GetDetailedQuiz):
    pass


class UpdateQuizRequest(Base):
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
            StringConstraints(
                min_length=3,
                max_length=500,
            ),
        ]
        | None
    ) = None
    is_public: bool | None = None

    @field_validator("title", "description", "is_public")
    @classmethod
    def prevent_explicit_null(cls, value):
        if value is None:
            raise ValueError("Null is not allowed for this field")

        return value
