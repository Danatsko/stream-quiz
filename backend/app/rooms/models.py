from sqlalchemy import BigInteger, String, ForeignKey, text, Index
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column

from app.core.models import Base, UUIDMixin, SoftDeleteMixin


class Room(Base, UUIDMixin, SoftDeleteMixin):
    __tablename__ = "room"

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

    @hybrid_property
    def search_vector(self):
        return f"{self.title} {self.description}"

    @search_vector.expression
    def search_vector(cls):
        return (cls.title + " " + cls.description).self_group()

    __table_args__ = (
        Index(
            "ix_room_search_trgm",
            text("(title || ' ' || description)"),
            postgresql_using="gin",
            postgresql_ops={"(title || ' ' || description)": "gin_trgm_ops"},
        ),
    )
