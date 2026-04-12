from uuid import UUID
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.db_repository import (
    create_user as db_repository_create_user,
    get_user_by_email as db_repository_get_user_by_email,
    get_user_by_id as db_repository_get_user_by_id,
    get_user_by_uuid as db_repository_get_user_by_uuid,
    get_user_uuids_by_ids as db_repository_get_user_uuids_by_ids,
    get_user_ids_by_uuids as db_repository_get_user_ids_by_uuids,
    get_users_by_ids as db_repository_get_users_by_ids,
)
from app.users.models import User


async def create_user(
    username: str,
    email: str,
    password: str,
    db_session: AsyncSession,
) -> User:
    try:
        user_db = await db_repository_create_user(
            username=username,
            email=email,
            password=password,
            db_session=db_session,
        )

        return user_db
    except IntegrityError as exc:
        msg = str(exc.orig)

        if "Key (email)=" in msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already exists",
            )
        else:
            raise exc


async def get_user_by_email(
    email: str,
    db_session: AsyncSession,
) -> User | None:
    user_db = await db_repository_get_user_by_email(
        email=email,
        db_session=db_session,
    )

    return user_db


async def get_user_by_id(
    id: int,
    db_session: AsyncSession,
) -> User | None:
    user_db = await db_repository_get_user_by_id(
        id=id,
        db_session=db_session,
    )

    return user_db


async def get_user_by_uuid(
    uuid: UUID,
    db_session: AsyncSession,
) -> User | None:
    user_db = await db_repository_get_user_by_uuid(
        uuid=uuid,
        db_session=db_session,
    )

    return user_db


async def get_user_uuids_by_ids(
    ids: set[int],
    db_session: AsyncSession,
) -> dict[int, UUID]:
    user_uuids_db = await db_repository_get_user_uuids_by_ids(
        ids=ids,
        db_session=db_session,
    )

    return user_uuids_db


async def get_user_ids_by_uuids(
    uuids: set[UUID],
    db_session: AsyncSession,
) -> dict[UUID, int]:
    user_ids_db = await db_repository_get_user_ids_by_uuids(
        uuids=uuids,
        db_session=db_session,
    )

    return user_ids_db


async def get_users_by_ids(
    ids: set[int],
    db_session: AsyncSession,
) -> dict[int, User]:
    users_db = await db_repository_get_users_by_ids(
        ids=ids,
        db_session=db_session,
    )

    return users_db


async def get_me(
    user_uuid: UUID,
    db_session: AsyncSession,
) -> dict[str, Any]:
    user_db = await db_repository_get_user_by_uuid(
        uuid=user_uuid,
        db_session=db_session,
    )

    if user_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    result = {
        "uuid": user_db.uuid,
        "username": user_db.username,
        "email": user_db.email,
    }

    return result


async def get_me_sessions(
    page: int,
    size: int,
    user_uuid: UUID,
    db_session: AsyncSession,
) -> dict[str, Any]:
    from app.sessions.service import get_user_sessions

    user_db = await db_repository_get_user_by_uuid(
        uuid=user_uuid,
        db_session=db_session,
    )

    if user_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    result = await get_user_sessions(
        page=page,
        size=size,
        user_id=user_db.id,
        db_session=db_session,
    )

    return result


async def get_me_session(
    user_uuid: UUID,
    session_uuid: UUID,
    db_session: AsyncSession,
) -> dict[str, Any]:
    from app.sessions.service import get_user_session

    user_db = await db_repository_get_user_by_uuid(
        uuid=user_uuid,
        db_session=db_session,
    )

    if user_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    result = await get_user_session(
        user_id=user_db.id,
        session_uuid=session_uuid,
        db_session=db_session,
    )

    return result
