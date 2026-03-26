from datetime import datetime, timezone, timedelta
import json
from typing import Any
from uuid import UUID

from redis.asyncio import Redis


async def set_session_info(
    room_uuid: UUID,
    session_uuid: UUID,
    time_seconds: int,
    questions_data: list[dict[str, Any]],
    redis_client: Redis,
) -> bool:
    current_time = datetime.now(tz=timezone.utc)
    end_time = current_time + timedelta(seconds=time_seconds)
    redis_session_info = {
        "room_uuid": str(room_uuid),
        "end_time_ts": end_time.timestamp(),
        "time_seconds": time_seconds,
        "questions": questions_data,
    }
    ttl = time_seconds + 300
    result = await redis_client.set(
        name=f"session:{session_uuid}:info",
        value=json.dumps(redis_session_info),
        ex=ttl,
    )

    return result is not None
