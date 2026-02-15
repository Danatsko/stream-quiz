import uuid
from typing import Annotated

from pydantic import StringConstraints, EmailStr

from app.core.schemas import Base

usernameAnnotated = Annotated[
    str,
    StringConstraints(
        min_length=3,
        max_length=30,
    ),
]


class GetMeResponse(Base):
    uuid: uuid.UUID
    username: usernameAnnotated
    email: EmailStr
