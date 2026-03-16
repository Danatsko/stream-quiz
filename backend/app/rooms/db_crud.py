from sqlalchemy import insert
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
