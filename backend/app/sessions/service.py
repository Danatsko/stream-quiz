from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.sessions.db_crud import (
    create_session as db_crud_create_session,
    update_session_by_uuid as db_crud_update_session_by_uuid,
    soft_delete_session_by_uuid as db_crud_soft_delete_session_by_uuid,
)
from app.sessions.models import Session


async def create_session(
    title: str,
    description: str,
    time_seconds: int,
    room_id: int,
    quiz_id: int,
    db_session: AsyncSession,
) -> Session:
    session_db = await db_crud_create_session(
        title=title,
        description=description,
        time_seconds=time_seconds,
        room_id=room_id,
        quiz_id=quiz_id,
        db_session=db_session,
    )

    return session_db


async def update_session_by_uuid(
    uuid: UUID,
    room_id: int,
    update_session_data: dict[str, Any],
    db_session: AsyncSession,
) -> bool:
    is_updated = await db_crud_update_session_by_uuid(
        uuid=uuid,
        room_id=room_id,
        update_session_data=update_session_data,
        db_session=db_session,
    )

    return is_updated


async def soft_delete_session_by_uuid(
    uuid: UUID,
    room_id: int,
    db_session: AsyncSession,
) -> bool:
    is_deleted = await db_crud_soft_delete_session_by_uuid(
        uuid=uuid,
        room_id=room_id,
        db_session=db_session,
    )

    return is_deleted
