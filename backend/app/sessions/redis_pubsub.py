import json
from typing import Any
from uuid import UUID

from redis.asyncio import Redis

from app.sessions.redis_store import (
    get_session_take_events_channel,
    get_session_host_events_channel,
)


async def publish_session_closed_event(
    session_uuid: UUID,
    redis_client: Redis,
) -> bool:
    take_channel = await get_session_take_events_channel(uuid=session_uuid)
    host_channel = await get_session_host_events_channel(uuid=session_uuid)
    event_payload = {
        "event": "session_closed",
        "message": "Session has been completed and closed",
    }
    message_dump = json.dumps(event_payload)

    async with redis_client.pipeline() as pipeline:
        await pipeline.publish(
            channel=take_channel,
            message=message_dump,
        )
        await pipeline.publish(
            channel=host_channel,
            message=message_dump,
        )
        results = await pipeline.execute()

    return sum(results) > 0


async def publish_session_host_event(
    session_uuid: UUID,
    event_payload: dict[str, Any],
    redis_client: Redis,
) -> bool:
    channel = await get_session_host_events_channel(uuid=session_uuid)
    receivers_count = await redis_client.publish(
        channel=channel,
        message=json.dumps(event_payload),
    )

    return receivers_count > 0
