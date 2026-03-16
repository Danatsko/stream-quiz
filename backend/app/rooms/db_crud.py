from sqlalchemy import insert, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.rooms.models import Room


async def create_room(
    title: str,
    description: str,
    creator_id: int,
    session: AsyncSession,
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
    result = await session.scalar(stmt)

    return result


async def get_rooms_total_count(
    user_id: int,
    session: AsyncSession,
) -> int:
    stmt = (
        select(func.count())
        .select_from(Room)
        .where(
            Room.creator_id == user_id,
            Room.deleted_at.is_(None),
        )
    )
    result = await session.scalar(stmt)

    return result or 0


async def get_rooms_list(
    user_id: int,
    limit: int,
    offset: int,
    session: AsyncSession,
) -> list[Room]:
    stmt = (
        select(Room)
        .where(
            Room.creator_id == user_id,
            Room.deleted_at.is_(None),
        )
        .limit(limit)
        .offset(offset)
    )
    result = await session.scalars(stmt)

    return list(result.all())
