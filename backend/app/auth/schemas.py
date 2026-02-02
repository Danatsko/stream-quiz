from typing import Annotated

from pydantic import StringConstraints, EmailStr

from app.core.schemas import Base

DEFAULT_USERNAME = "User"
usernameAnnotated = Annotated[
    str,
    StringConstraints(
        min_length=3,
        max_length=30,
    ),
]
passwordAnnotated = Annotated[
    str,
    StringConstraints(min_length=8),
]


class RegistrationRequest(Base):
    username: usernameAnnotated | None = DEFAULT_USERNAME
    email: EmailStr
    password: passwordAnnotated


class RegistrationResponse(Base):
    pass
