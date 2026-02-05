import uuid
from typing import Annotated

from pydantic import StringConstraints

from app.core.schemas import Base

usernameAnnotated = Annotated[
    str,
    StringConstraints(
        min_length=3,
        max_length=30,
    ),
]


class GETMeResponse(Base):
    uuid: uuid.UUID
    username: usernameAnnotated
    email: usernameAnnotated
