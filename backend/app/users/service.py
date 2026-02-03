from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.db_crud import (
    create_user as db_crud_create_user,
    get_user_by_email as db_crud_get_user_by_email,
)
from app.users.models import User


async def create_user(
    username: str, email: str, password: str, session: AsyncSession
) -> User:
    try:
        user_db = await db_crud_create_user(
            username=username,
            email=email,
            password=password,
            session=session,
        )

        return user_db
    except IntegrityError as exc:
        msg = str(exc.orig)

        if "Key (id)=" in msg:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Something went wrong",
            )
        elif "Key (uuid)=" in msg:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Something went wrong",
            )
        elif "Key (email)=" in msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already exists",
            )
        else:
            raise exc


async def get_user_by_email(email: str, session: AsyncSession) -> User | None:
    user_db = await db_crud_get_user_by_email(
        email=email,
        session=session,
    )

    return user_db
