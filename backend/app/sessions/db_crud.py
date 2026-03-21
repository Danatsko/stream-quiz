from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.sessions.models import Session


async def create_session(
    title: str,
    description: str,
    time_seconds: int,
    room_id: int,
    quiz_id: int,
    session: AsyncSession,
) -> Session:
    stmt = (
        insert(Session)
        .values(
            room_id=room_id,
            quiz_id=quiz_id,
            title=title,
            description=description,
            time_seconds=time_seconds,
        )
        .returning(Session)
    )
    result = await session.scalar(stmt)

    return result
