from sqlalchemy import BigInteger, String, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.models import Base, UUIDMixin, SoftDeleteMixin


class Room(Base, UUIDMixin, SoftDeleteMixin):
    __tablename__ = "room"

    creator_id: Mapped[int] = mapped_column(
        BigInteger(),
        ForeignKey(
            "user.id",
            onupdate="CASCADE",
            ondelete="CASCADE",
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
