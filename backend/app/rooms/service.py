from uuid import UUID
from typing import Any

from arq import ArqRedis
from fastapi import HTTPException, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.rooms.db_crud import (
    create_room as db_crud_create_room,
    get_rooms_total_count,
    get_rooms_list,
    update_room_by_uuid,
    soft_delete_room_by_uuid,
    get_room_by_uuid,
)
from app.sessions.service import (
    create_session as sessions_service_create_session,
    get_sessions as sessions_service_get_sessions,
    get_session as sessions_service_get_session,
    update_session as sessions_service_update_session,
    delete_session as sessions_service_delete_session,
    start_session as sessions_service_start_session,
)
from app.users.service import get_user_by_uuid


async def create_room(
    title: str,
    description: str,
    user_uuid: UUID,
    db_session: AsyncSession,
) -> dict[str, Any]:
    user_db = await get_user_by_uuid(
        uuid=user_uuid,
        db_session=db_session,
    )
    room_db = await db_crud_create_room(
        title=title,
        description=description,
        creator_id=user_db.id,
        db_session=db_session,
    )
    result = {"uuid": room_db.uuid}

    return result


async def get_rooms(
    page: int,
    size: int,
    user_uuid: UUID,
    db_session: AsyncSession,
) -> dict[str, Any]:
    offset = (page - 1) * size
    user_db = await get_user_by_uuid(
        uuid=user_uuid,
        db_session=db_session,
    )
    total_rooms_db = await get_rooms_total_count(
        user_id=user_db.id,
        db_session=db_session,
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
        db_session=db_session,
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


async def get_room(
    room_uuid: UUID,
    user_uuid: UUID,
    db_session: AsyncSession,
) -> dict[str, Any]:
    user_db = await get_user_by_uuid(
        uuid=user_uuid,
        db_session=db_session,
    )
    room_db = await get_room_by_uuid(
        uuid=room_uuid,
        user_id=user_db.id,
        db_session=db_session,
    )

    if room_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )

    result = {
        "creator_uuid": user_db.uuid,
        "uuid": room_db.uuid,
        "title": room_db.title,
        "description": room_db.description,
        "created_at": room_db.created_at,
        "updated_at": room_db.updated_at,
    }

    return result


async def update_room(
    room_uuid: UUID,
    user_uuid: UUID,
    update_room_data: dict[str, Any],
    db_session: AsyncSession,
) -> None:
    if not update_room_data:
        return

    user_db = await get_user_by_uuid(
        uuid=user_uuid,
        db_session=db_session,
    )
    is_updated = await update_room_by_uuid(
        uuid=room_uuid,
        user_id=user_db.id,
        update_room_data=update_room_data,
        db_session=db_session,
    )

    if not is_updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )


async def delete_room(
    room_uuid: UUID,
    user_uuid: UUID,
    db_session: AsyncSession,
) -> None:
    user_db = await get_user_by_uuid(
        uuid=user_uuid,
        db_session=db_session,
    )
    is_deleted = await soft_delete_room_by_uuid(
        uuid=room_uuid,
        user_id=user_db.id,
        db_session=db_session,
    )

    if not is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )


async def create_session(
    title: str,
    description: str,
    time_seconds: int,
    quiz_uuid: UUID,
    room_uuid: UUID,
    user_uuid: UUID,
    db_session: AsyncSession,
) -> dict[str, Any]:
    user_db = await get_user_by_uuid(
        uuid=user_uuid,
        db_session=db_session,
    )
    room_db = await get_room_by_uuid(
        uuid=room_uuid,
        user_id=user_db.id,
        db_session=db_session,
    )

    if room_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )

    result = await sessions_service_create_session(
        title=title,
        description=description,
        time_seconds=time_seconds,
        room_id=room_db.id,
        user_id=user_db.id,
        quiz_uuid=quiz_uuid,
        db_session=db_session,
    )

    return result


async def get_sessions(
    page: int,
    size: int,
    room_uuid: UUID,
    user_uuid: UUID,
    db_session: AsyncSession,
) -> dict[str, Any]:
    user_db = await get_user_by_uuid(
        uuid=user_uuid,
        db_session=db_session,
    )
    room_db = await get_room_by_uuid(
        uuid=room_uuid,
        user_id=user_db.id,
        db_session=db_session,
    )

    if room_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )

    result = await sessions_service_get_sessions(
        page=page,
        size=size,
        room_id=room_db.id,
        user_id=user_db.id,
        room_uuid=room_db.uuid,
        db_session=db_session,
    )

    return result


async def get_session(
    room_uuid: UUID,
    session_uuid: UUID,
    user_uuid: UUID,
    db_session: AsyncSession,
) -> dict[str, Any]:
    user_db = await get_user_by_uuid(
        uuid=user_uuid,
        db_session=db_session,
    )
    room_db = await get_room_by_uuid(
        uuid=room_uuid,
        user_id=user_db.id,
        db_session=db_session,
    )

    if room_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )

    result = await sessions_service_get_session(
        room_id=room_db.id,
        user_id=user_db.id,
        room_uuid=room_db.uuid,
        session_uuid=session_uuid,
        db_session=db_session,
    )

    return result


async def update_session(
    room_uuid: UUID,
    session_uuid: UUID,
    user_uuid: UUID,
    update_session_data: dict[str, Any],
    db_session: AsyncSession,
) -> None:
    if not update_session_data:
        return

    user_db = await get_user_by_uuid(
        uuid=user_uuid,
        db_session=db_session,
    )
    room_db = await get_room_by_uuid(
        uuid=room_uuid,
        user_id=user_db.id,
        db_session=db_session,
    )

    if room_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )

    await sessions_service_update_session(
        room_id=room_db.id,
        user_id=user_db.id,
        room_uuid=room_db.uuid,
        session_uuid=session_uuid,
        update_session_data=update_session_data,
        db_session=db_session,
    )


async def delete_session(
    room_uuid: UUID,
    session_uuid: UUID,
    user_uuid: UUID,
    db_session: AsyncSession,
) -> None:
    user_db = await get_user_by_uuid(
        uuid=user_uuid,
        db_session=db_session,
    )
    room_db = await get_room_by_uuid(
        uuid=room_uuid,
        user_id=user_db.id,
        db_session=db_session,
    )

    if room_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )

    await sessions_service_delete_session(
        room_id=room_db.id,
        session_uuid=session_uuid,
        db_session=db_session,
    )


async def start_session(
    room_uuid: UUID,
    session_uuid: UUID,
    user_uuid: UUID,
    db_session: AsyncSession,
    redis_client: Redis,
    arq_pool: ArqRedis,
) -> None:
    user_db = await get_user_by_uuid(
        uuid=user_uuid,
        db_session=db_session,
    )
    room_db = await get_room_by_uuid(
        uuid=room_uuid,
        user_id=user_db.id,
        db_session=db_session,
    )

    if room_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )

    await sessions_service_start_session(
        room_id=room_db.id,
        user_id=user_db.id,
        room_uuid=room_db.uuid,
        session_uuid=session_uuid,
        db_session=db_session,
        redis_client=redis_client,
        arq_pool=arq_pool,
    )
