from uuid import UUID
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.rooms.db_crud import (
    create_room as db_crud_create_room,
    get_rooms_total_count,
    get_rooms_list,
)
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


async def get_rooms(
    page: int,
    size: int,
    user_uuid: UUID,
    session: AsyncSession,
) -> dict[str, Any]:
    offset = (page - 1) * size
    user_db = await get_user_by_uuid(
        uuid=user_uuid,
        session=session,
    )
    total_rooms_db = await get_rooms_total_count(
        user_id=user_db.id,
        session=session,
    )

    if total_rooms_db == 0:
        result = {
            "rooms": [],
            "total_rooms": total_rooms_db,
            "page": page,
            "size": size,
            "total_pages": 0,
        }

        return result

    rooms_db = await get_rooms_list(
        user_id=user_db.id,
        limit=size,
        offset=offset,
        session=session,
    )
    total_pages = (total_rooms_db + size - 1) // size
    rooms = []

    for room_db in rooms_db:
        rooms.append(
            {
                "uuid": room_db.uuid,
                "title": room_db.title,
                "description": room_db.description,
                "creator_uuid": user_db.uuid,
                "created_at": room_db.created_at,
                "updated_at": room_db.updated_at,
            }
        )

    result = {
        "rooms": rooms,
        "total_rooms": total_rooms_db,
        "page": page,
        "size": size,
        "total_pages": total_pages,
    }

    return result
