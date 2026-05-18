from sqlalchemy import BigInteger, String, Boolean, ForeignKey, false, text, Index
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models import Base, UUIDMixin, SoftDeleteMixin


class Quiz(Base, UUIDMixin, SoftDeleteMixin):
    __tablename__ = "quiz"

    creator_id: Mapped[int] = mapped_column(
        BigInteger(),
        ForeignKey(
            "user.id",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        server_default=text("''"),
    )
    is_public: Mapped[bool] = mapped_column(
        Boolean(),
        nullable=False,
        server_default=false(),
    )

    questions: Mapped[list["QuizQuestion"]] = relationship(
        back_populates="quiz",
        cascade="all, delete-orphan",
        lazy="raise_on_sql",
    )

    @hybrid_property
    def search_vector(self):
        return f"{self.title} {self.description}"

    @search_vector.expression
    def search_vector(cls):
        return (cls.title + " " + cls.description).self_group()

    __table_args__ = (
        Index(
            "ix_quiz_search_trgm",
            text("(title || ' ' || description)"),
            postgresql_using="gin",
            postgresql_ops={"(title || ' ' || description)": "gin_trgm_ops"},
        ),
    )


class QuizQuestion(Base, UUIDMixin):
    __tablename__ = "quiz_question"

    quiz_id: Mapped[int] = mapped_column(
        BigInteger(),
        ForeignKey(
            "quiz.id",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )
    text: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )
    is_multiple_answers: Mapped[bool] = mapped_column(
        Boolean(),
        nullable=False,
    )

    quiz: Mapped["Quiz"] = relationship(
        back_populates="questions",
        lazy="raise_on_sql",
    )
    options: Mapped[list["QuizQuestionOption"]] = relationship(
        back_populates="question",
        cascade="all, delete-orphan",
        lazy="raise_on_sql",
    )


class QuizQuestionOption(Base, UUIDMixin):
    __tablename__ = "quiz_question_option"

    quiz_question_id: Mapped[int] = mapped_column(
        BigInteger(),
        ForeignKey(
            "quiz_question.id",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )
    text: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )
    is_correct: Mapped[bool] = mapped_column(
        Boolean(),
        nullable=False,
    )

    question: Mapped["QuizQuestion"] = relationship(
        back_populates="options",
        lazy="raise_on_sql",
    )
