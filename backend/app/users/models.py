from sqlalchemy import text, String, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.core.models import Base, UUIDMixin, SoftDeleteMixin


class User(Base, UUIDMixin, SoftDeleteMixin):
    __tablename__ = "user"

    username: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )
    email: Mapped[str] = mapped_column(
        String(),
        nullable=False,
    )
    password: Mapped[str] = mapped_column(
        String(),
        nullable=False,
    )

    __table_args__ = (
        Index(
            "uq_user_email_not_deleted",
            "email",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )
