import uuid
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.db_crud import (
    create_user as db_crud_create_user,
    get_user_by_email as db_crud_get_user_by_email,
    get_user_by_id as db_crud_get_user_by_id,
    get_user_by_uuid as db_crud_get_user_by_uuid,
    get_user_uuids_by_ids as db_crud_get_user_uuids_by_ids,
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


async def get_user_by_id(id: int, session: AsyncSession) -> User | None:
    user_db = await db_crud_get_user_by_id(
        id=id,
        session=session,
    )

    return user_db


async def get_user_by_uuid(uuid: uuid.UUID, session: AsyncSession) -> User | None:
    user_db = await db_crud_get_user_by_uuid(
        uuid=uuid,
        session=session,
    )

    return user_db


async def get_user_uuids_by_ids(
    ids: set[int], session: AsyncSession
) -> dict[int, uuid.UUID]:
    user_uuids_db = await db_crud_get_user_uuids_by_ids(
        ids=ids,
        session=session,
    )

    return user_uuids_db


async def get_me(uuid: uuid.UUID, session: AsyncSession) -> dict[str, Any]:
    user_db = await db_crud_get_user_by_uuid(
        uuid=uuid,
        session=session,
    )

    result = {
        "uuid": user_db.uuid,
        "username": user_db.username,
        "email": user_db.email,
    }

    return result
