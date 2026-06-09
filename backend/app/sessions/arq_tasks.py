from typing import Any
from uuid import UUID

from app.core.db import get_db_session_factory
from app.core.redis import get_redis_client
from app.sessions.service import finalize_session


async def auto_close_session(
    ctx: dict[str, Any],
    session_uuid: UUID,
    room_id: int,
) -> None:
    redis_client = await get_redis_client()
    db_session_factory = await get_db_session_factory()

    async with db_session_factory.begin() as db_session:
        await finalize_session(
            session_uuid=session_uuid,
            room_id=room_id,
            db_session=db_session,
            redis_client=redis_client,
        )
