import json
from uuid import UUID

from redis.asyncio import Redis

from app.sessions.redis_store import get_session_events_channel


async def publish_session_closed_event(
    session_uuid: UUID,
    redis_client: Redis,
) -> bool:
    channel = await get_session_events_channel(uuid=session_uuid)
    event_payload = {
        "event": "session_closed",
        "message": "Session has been completed and closed",
    }
    receivers_count = await redis_client.publish(
        channel=channel,
        message=json.dumps(event_payload),
    )

    return receivers_count > 0
