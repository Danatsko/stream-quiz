import json
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from redis.asyncio import Redis

from app.auth.dependencies import get_ws_auth_context
from app.core.redis import get_redis_client
from app.sessions.service import get_ws_sync_state, process_ws_event
from app.sessions.ws_manager import session_manager

sessions_ws_router = APIRouter()


@sessions_ws_router.websocket("/{session_uuid}")
async def session_websocket(
    websocket: WebSocket,
    session_uuid: UUID,
    auth_context: Annotated[dict[str, Any], Depends(get_ws_auth_context)],
    redis_client: Annotated[Redis, Depends(get_redis_client)],
) -> None:
    await websocket.accept()

    user_uuid = auth_context["user_uuid"]

    await session_manager.connect(
        session_uuid=session_uuid,
        user_uuid=user_uuid,
        websocket=websocket,
    )

    try:
        sync_state_data = await get_ws_sync_state(
            session_uuid=session_uuid,
            user_uuid=user_uuid,
            redis_client=redis_client,
        )

        if not sync_state_data:
            await websocket.close(
                code=1008,
                reason="Session is not active",
            )
            return

        await websocket.send_json(
            {
                "event": "sync_state",
                "end_time_ts": sync_state_data["end_time_ts"],
                "questions": sync_state_data["questions"],
                "total_questions": sync_state_data["total_questions"],
                "answered_questions": sync_state_data["answered_questions"],
            }
        )

        while True:
            try:
                data = await websocket.receive_json()

                response_payload = await process_ws_event(
                    event_data=data,
                    session_uuid=session_uuid,
                    user_uuid=user_uuid,
                    redis_client=redis_client,
                )

                if response_payload:
                    await websocket.send_json(response_payload)
            except json.JSONDecodeError:
                await websocket.send_json(
                    {
                        "event": "error",
                        "message": "Payload must be a valid JSON",
                    }
                )
            except RuntimeError:
                break
    except WebSocketDisconnect:
        pass
    finally:
        await session_manager.disconnect(
            session_uuid=session_uuid,
            user_uuid=user_uuid,
        )
