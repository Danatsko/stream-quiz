from typing import Annotated

from pydantic import StringConstraints, EmailStr

from app.core.schemas import Base

DEFAULT_USERNAME = "User"


class AuthBase(Base):
    email: EmailStr
    password: Annotated[
        str,
        StringConstraints(min_length=8),
    ]


class RegistrationRequest(AuthBase):
    username: Annotated[
        str,
        StringConstraints(
            min_length=3,
            max_length=30,
        ),
    ] = DEFAULT_USERNAME


class LoginRequest(AuthBase):
    pass
