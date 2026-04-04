from typing import Any
from uuid import UUID

from fastapi import WebSocket


class SessionConnectionManager:
    def __init__(self) -> None:
        self.active_connections: dict[UUID, dict[UUID, WebSocket]] = {}

    async def connect(
        self,
        session_uuid: UUID,
        user_uuid: UUID,
        websocket: WebSocket,
    ) -> None:
        if session_uuid not in self.active_connections:
            self.active_connections[session_uuid] = {}

        existing_ws = self.active_connections[session_uuid].get(user_uuid)

        if existing_ws:
            try:
                await existing_ws.close()
            except Exception:
                pass

        self.active_connections[session_uuid][user_uuid] = websocket

    def disconnect(
        self,
        session_uuid: UUID,
        user_uuid: UUID,
    ) -> None:
        if session_uuid in self.active_connections:
            self.active_connections[session_uuid].pop(
                user_uuid,
                None,
            )

            if not self.active_connections[session_uuid]:
                del self.active_connections[session_uuid]

    async def broadcast_to_session(
        self,
        session_uuid: UUID,
        message: dict[str, Any],
    ) -> None:
        if session_uuid in self.active_connections:
            for connection in self.active_connections[session_uuid].values():
                try:
                    await connection.send_json(message)
                except Exception:
                    pass


session_manager = SessionConnectionManager()
