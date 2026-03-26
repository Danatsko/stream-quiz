from typing import Any

from app.core.db import get_db_session_factory
from app.sessions.db_crud import complete_session_by_id


async def auto_close_session(
    ctx: dict[str, Any],
    session_id: int,
    room_id: int,
) -> None:
    # TODO: fetch member answers from Redis
    # TODO: bulk insert member answers to DB
    # TODO: clear session data from Redis after completion

    db_session_factory = await get_db_session_factory()

    async with db_session_factory.begin() as db_session:
        await complete_session_by_id(
            id=session_id,
            room_id=room_id,
            db_session=db_session,
        )
