import json
from asyncio import CancelledError
from uuid import UUID

from redis.asyncio import Redis

from app.sessions.redis_store import get_session_events_channel
from app.sessions.ws_manager import session_manager


async def global_redis_pubsub_listener(redis_client: Redis) -> None:
    pubsub = redis_client.pubsub()
    match_pattern = await get_session_events_channel(uuid="*")

    await pubsub.psubscribe(match_pattern)

    try:
        async for message in pubsub.listen():
            if message["type"] == "pmessage":
                data = json.loads(message["data"])

                channel_name = (
                    message["channel"].decode()
                    if isinstance(message["channel"], bytes)
                    else message["channel"]
                )
                session_uuid_str = channel_name.split(":")[1]

                try:
                    session_uuid = UUID(session_uuid_str)
                except ValueError:
                    continue

                await session_manager.broadcast_to_session(
                    session_uuid=session_uuid,
                    message=data,
                )

                if data.get("event") == "session_closed":
                    await session_manager.close_session_connections(
                        session_uuid=session_uuid
                    )
    except CancelledError:
        pass
    except Exception:
        pass
    finally:
        await pubsub.punsubscribe(match_pattern)
        await pubsub.close()
