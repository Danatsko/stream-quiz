from uuid import UUID
from typing import Annotated

from pydantic import StringConstraints, EmailStr

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


class GetMeResponse(UserBase):
    pass
