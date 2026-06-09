from datetime import datetime

from sqlalchemy import ForeignKey, BigInteger, String, Boolean, DateTime, false
from sqlalchemy.orm import Mapped, mapped_column

from app.core.models import Base


class RefreshToken(Base):
    __tablename__ = "refresh_token"

    user_id: Mapped[int] = mapped_column(
        BigInteger(),
        ForeignKey(
            "user.id",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )
    token: Mapped[str] = mapped_column(
        String(),
        unique=True,
        nullable=False,
    )
    is_revoked: Mapped[bool] = mapped_column(
        Boolean(),
        nullable=False,
        server_default=false(),
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
