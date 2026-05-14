import json
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_ws_auth_context
from app.core.db import get_db_session
from app.core.redis import get_redis_client
from app.sessions.service import (
    get_ws_take_sync_state,
    process_ws_take_event,
    get_ws_host_sync_state,
    is_session_creator,
    process_ws_host_event,
)
from app.sessions.ws_manager import session_manager

sessions_ws_router = APIRouter()


@sessions_ws_router.websocket("/{session_uuid}/take")
async def session_take(
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
        take_sync_state_data = await get_ws_take_sync_state(
            session_uuid=session_uuid,
            user_uuid=user_uuid,
            redis_client=redis_client,
        )

        if not take_sync_state_data:
            await websocket.close(
                code=1008,
                reason="Session is not active",
            )

            return

        await websocket.send_json(
            {
                "event": "sync_state",
                "end_time_ts": take_sync_state_data["end_time_ts"],
                "questions": take_sync_state_data["questions"],
                "total_questions": take_sync_state_data["total_questions"],
                "answered_questions": take_sync_state_data["answered_questions"],
            }
        )

        while True:
            try:
                data = await websocket.receive_json()
                response_payload = await process_ws_take_event(
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


@sessions_ws_router.websocket("/{session_uuid}/host")
async def session_host(
    websocket: WebSocket,
    session_uuid: UUID,
    auth_context: Annotated[dict[str, Any], Depends(get_ws_auth_context)],
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    redis_client: Annotated[Redis, Depends(get_redis_client)],
) -> None:
    await websocket.accept()

    user_uuid = auth_context["user_uuid"]
    is_creator = await is_session_creator(
        session_uuid=session_uuid,
        user_uuid=user_uuid,
        db_session=db_session,
    )

    if not is_creator:
        await websocket.close(
            code=1008,
            reason="Not the session host",
        )
        return

    await session_manager.connect(
        session_uuid=session_uuid,
        user_uuid=user_uuid,
        websocket=websocket,
        role="host",
    )

    try:
        host_sync_state_data = await get_ws_host_sync_state(
            session_uuid=session_uuid,
            db_session=db_session,
            redis_client=redis_client,
        )

        if not host_sync_state_data:
            await websocket.close(
                code=1008,
                reason="Session is not active",
            )

            return

        await websocket.send_json(
            {
                "event": "sync_state",
                "questions": host_sync_state_data["questions"],
                "total_questions": host_sync_state_data["total_questions"],
                "end_time_ts": host_sync_state_data["end_time_ts"],
                "members": host_sync_state_data["members"],
                "total_members": host_sync_state_data["total_members"],
            }
        )

        while True:
            try:
                data = await websocket.receive_json()
                response_payload = await process_ws_host_event(
                    event_data=data,
                    session_uuid=session_uuid,
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
            role="host",
        )
