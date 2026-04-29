from typing import Any
from uuid import UUID

from fastapi import WebSocket


class SessionConnectionManager:
    def __init__(self) -> None:
        self._active_connections: dict[UUID, dict[UUID, WebSocket]] = {}

    async def connect(
        self,
        session_uuid: UUID,
        user_uuid: UUID,
        websocket: WebSocket,
    ) -> None:
        if session_uuid not in self._active_connections:
            self._active_connections[session_uuid] = {}

        existing_ws = self._active_connections[session_uuid].get(user_uuid)

        if existing_ws:
            try:
                await existing_ws.close()
            except Exception:
                pass

        self._active_connections[session_uuid][user_uuid] = websocket

    async def disconnect(
        self,
        session_uuid: UUID,
        user_uuid: UUID,
    ) -> None:
        if session_uuid in self._active_connections:
            self._active_connections[session_uuid].pop(
                user_uuid,
                None,
            )

            if not self._active_connections[session_uuid]:
                self._active_connections.pop(
                    session_uuid,
                    None,
                )

    async def close_session_connections(
        self,
        session_uuid: UUID,
        code: int,
        reason: str,
    ) -> None:
        if session_uuid in self._active_connections:
            connections = list(self._active_connections[session_uuid].values())

            for connection in connections:
                try:
                    await connection.close(
                        code=code,
                        reason=reason,
                    )
                except Exception:
                    pass

            self._active_connections.pop(
                session_uuid,
                None,
            )

    async def broadcast_to_session(
        self,
        session_uuid: UUID,
        message: dict[str, Any],
    ) -> None:
        if session_uuid in self._active_connections:
            for connection in self._active_connections[session_uuid].values():
                try:
                    await connection.send_json(message)
                except Exception:
                    pass


session_manager = SessionConnectionManager()
