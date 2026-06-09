from typing import Any
from uuid import UUID

from sqlalchemy import insert, select, update, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.rooms.models import Room


async def _rooms_search_filter(q: str | None = None) -> list[Any]:
    conditions = []

    if q is not None:
        conditions.append(
            or_(
                Room.search_vector.ilike(f"%{q}%"),
                Room.search_vector.bool_op("%>")(q),
            )
        )

    return conditions


async def create_room(
    title: str,
    description: str,
    creator_id: int,
    db_session: AsyncSession,
) -> Room:
    stmt = (
        insert(Room)
        .values(
            creator_id=creator_id,
            title=title,
            description=description,
        )
        .returning(Room)
    )
    result = await db_session.scalar(stmt)

    return result


async def get_rooms_total_count(
    user_id: int,
    db_session: AsyncSession,
    q: str | None = None,
) -> int:
    search_filter = await _rooms_search_filter(q=q)
    stmt = (
        select(func.count())
        .select_from(Room)
        .where(
            *search_filter,
            Room.creator_id == user_id,
            Room.deleted_at.is_(None),
        )
    )
    result = await db_session.scalar(stmt)

    return result or 0


async def get_rooms_list(
    user_id: int,
    limit: int,
    offset: int,
    db_session: AsyncSession,
    q: str | None = None,
) -> list[Room]:
    search_filter = await _rooms_search_filter(q=q)
    stmt = (
        select(Room)
        .where(
            *search_filter,
            Room.creator_id == user_id,
            Room.deleted_at.is_(None),
        )
        .order_by(Room.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db_session.scalars(stmt)

    return list(result.all())


async def get_room_by_uuid(
    uuid: UUID,
    user_id: int,
    db_session: AsyncSession,
) -> Room | None:
    stmt = select(Room).where(
        Room.uuid == uuid,
        Room.creator_id == user_id,
        Room.deleted_at.is_(None),
    )
    result = await db_session.scalar(stmt)

    return result


async def update_room_by_uuid(
    uuid: UUID,
    user_id: int,
    update_room_data: dict[str, Any],
    db_session: AsyncSession,
) -> bool:
    if not update_room_data:
        return False

    stmt = (
        update(Room)
        .where(
            Room.uuid == uuid,
            Room.creator_id == user_id,
            Room.deleted_at.is_(None),
        )
        .values(**update_room_data)
    )
    result = await db_session.execute(stmt)

    return result.rowcount == 1


async def soft_delete_room_by_uuid(
    uuid: UUID,
    user_id: int,
    db_session: AsyncSession,
) -> bool:
    stmt = (
        update(Room)
        .where(
            Room.uuid == uuid,
            Room.creator_id == user_id,
            Room.deleted_at.is_(None),
        )
        .values(deleted_at=func.now())
    )
    result = await db_session.execute(stmt)

    return result.rowcount == 1


async def check_is_room_creator(
    room_id: int,
    user_id: int,
    db_session: AsyncSession,
) -> bool:
    stmt = select(Room.id).where(
        Room.id == room_id,
        Room.creator_id == user_id,
        Room.deleted_at.is_(None),
    )
    result = await db_session.scalar(stmt)

    return result is not None
