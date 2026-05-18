import enum
from sqlalchemy import (
    BigInteger,
    Integer,
    String,
    ForeignKey,
    text,
    Enum,
    Boolean,
    CheckConstraint,
    UniqueConstraint,
    Index,
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models import Base, UUIDMixin, SoftDeleteMixin


class SessionStatus(str, enum.Enum):
    waiting = "waiting"
    active = "active"
    completed = "completed"


class Session(Base, UUIDMixin, SoftDeleteMixin):
    __tablename__ = "session"

    room_id: Mapped[int] = mapped_column(
        BigInteger(),
        ForeignKey(
            "room.id",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )
    quiz_id: Mapped[int] = mapped_column(
        BigInteger(),
        ForeignKey(
            "quiz.id",
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
    time_seconds: Mapped[int] = mapped_column(
        Integer(),
        nullable=False,
    )
    status: Mapped[SessionStatus] = mapped_column(
        Enum(
            SessionStatus,
            name="session_status",
            create_constraint=False,
        ),
        nullable=False,
        server_default=text("'waiting'"),
    )

    questions: Mapped[list["SessionQuestion"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        lazy="raise_on_sql",
    )
    members: Mapped[list["SessionMember"]] = relationship(
        back_populates="session",
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
        CheckConstraint(
            "time_seconds > 0",
            name="chk_positive_time_seconds",
        ),
        CheckConstraint(
            "time_seconds <= 604800",
            name="chk_less_equal_week_time_seconds",
        ),
        Index(
            "ix_session_search_trgm",
            text("(title || ' ' || description)"),
            postgresql_using="gin",
            postgresql_ops={"(title || ' ' || description)": "gin_trgm_ops"},
        ),
    )


class SessionQuestion(Base, UUIDMixin):
    __tablename__ = "session_question"

    session_id: Mapped[int] = mapped_column(
        BigInteger(),
        ForeignKey(
            "session.id",
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

    session: Mapped["Session"] = relationship(
        back_populates="questions",
        lazy="raise_on_sql",
    )
    options: Mapped[list["SessionQuestionOption"]] = relationship(
        back_populates="question",
        cascade="all, delete-orphan",
        lazy="raise_on_sql",
    )
    answers: Mapped[list["SessionMemberAnswer"]] = relationship(
        back_populates="question",
        cascade="all, delete-orphan",
        lazy="raise_on_sql",
    )


class SessionQuestionOption(Base, UUIDMixin):
    __tablename__ = "session_question_option"

    session_question_id: Mapped[int] = mapped_column(
        BigInteger(),
        ForeignKey(
            "session_question.id",
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

    question: Mapped["SessionQuestion"] = relationship(
        back_populates="options",
        lazy="raise_on_sql",
    )
    answers: Mapped[list["SessionMemberAnswer"]] = relationship(
        back_populates="option",
        cascade="all, delete-orphan",
        lazy="raise_on_sql",
    )


class SessionMember(Base, UUIDMixin):
    __tablename__ = "session_member"

    session_id: Mapped[int] = mapped_column(
        BigInteger(),
        ForeignKey(
            "session.id",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger(),
        ForeignKey(
            "user.id",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    session: Mapped["Session"] = relationship(
        back_populates="members",
        lazy="raise_on_sql",
    )
    answers: Mapped[list["SessionMemberAnswer"]] = relationship(
        back_populates="member",
        cascade="all, delete-orphan",
        lazy="raise_on_sql",
    )

    __table_args__ = (
        UniqueConstraint(
            "session_id", "user_id", name="uq_session_member_session_user"
        ),
    )


class SessionMemberAnswer(Base, UUIDMixin):
    __tablename__ = "session_member_answer"

    session_question_id: Mapped[int] = mapped_column(
        BigInteger(),
        ForeignKey(
            "session_question.id",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )
    session_question_option_id: Mapped[int] = mapped_column(
        BigInteger(),
        ForeignKey(
            "session_question_option.id",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )
    session_member_id: Mapped[int] = mapped_column(
        BigInteger(),
        ForeignKey(
            "session_member.id",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    question: Mapped["SessionQuestion"] = relationship(
        back_populates="answers",
        lazy="raise_on_sql",
    )
    option: Mapped["SessionQuestionOption"] = relationship(
        back_populates="answers",
        lazy="raise_on_sql",
    )
    member: Mapped["SessionMember"] = relationship(
        back_populates="answers",
        lazy="raise_on_sql",
    )

    __table_args__ = (
        UniqueConstraint(
            "session_member_id",
            "session_question_id",
            "session_question_option_id",
            name="uq_session_member_answer",
        ),
    )
