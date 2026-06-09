from datetime import datetime
from uuid import UUID

from sqlalchemy import BigInteger, Uuid, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(
        BigInteger(),
        primary_key=True,
        autoincrement=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class UUIDMixin:
    uuid: Mapped[UUID] = mapped_column(
        Uuid(),
        unique=True,
        nullable=False,
        server_default=func.uuidv7(),
    )


class SoftDeleteMixin:
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
