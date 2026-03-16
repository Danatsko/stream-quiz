from uuid import UUID
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.rooms.db_crud import create_room as db_crud_create_room
from app.users.service import get_user_by_uuid


async def create_room(
    title: str,
    description: str,
    user_uuid: UUID,
    session: AsyncSession,
) -> dict[str, Any]:
    user_db = await get_user_by_uuid(
        uuid=user_uuid,
        session=session,
    )
    room_db = await db_crud_create_room(
        title=title,
        description=description,
        creator_id=user_db.id,
        session=session,
    )
    result = {"uuid": room_db.uuid}

    return result
