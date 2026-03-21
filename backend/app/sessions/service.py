from sqlalchemy.ext.asyncio import AsyncSession

from app.sessions.db_crud import create_session as db_crud_create_session
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
