import json
from uuid import UUID

from fastapi import WebSocket, WebSocketDisconnect
from redis.asyncio import Redis

from app.sessions.redis_crud import get_session_events_channel


async def redis_pubsub_listener(
    session_uuid: UUID,
    websocket: WebSocket,
    redis_client: Redis,
) -> None:
    pubsub = redis_client.pubsub()
    channel = await get_session_events_channel(uuid=session_uuid)

    await pubsub.subscribe(channel)

    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                data = json.loads(message["data"])

                try:
                    await websocket.send_json(data)

                    if data.get("event") == "session_closed":
                        await websocket.close(
                            code=1000,
                            reason="Session closed by server",
                        )

                        break
                except (WebSocketDisconnect, RuntimeError):
                    break
    except Exception:
        pass
    finally:
        await pubsub.unsubscribe(channel)
        await pubsub.close()
