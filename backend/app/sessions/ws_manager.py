from typing import Any, Literal
from uuid import UUID

from fastapi import WebSocket

RoleType = Literal[
    "member",
    "host",
]


class SessionConnectionManager:
    def __init__(self) -> None:
        self._active_connections: dict[UUID, dict[RoleType, dict[UUID, WebSocket]]] = {}

    async def connect(
        self,
        session_uuid: UUID,
        user_uuid: UUID,
        websocket: WebSocket,
        role: RoleType = "member",
    ) -> None:
        if session_uuid not in self._active_connections:
            self._active_connections[session_uuid] = {"member": {}, "host": {}}

        existing_ws = self._active_connections[session_uuid][role].get(user_uuid)

        if existing_ws:
            try:
                await existing_ws.close()
            except Exception:
                pass

        self._active_connections[session_uuid][role][user_uuid] = websocket

    async def disconnect(
        self,
        session_uuid: UUID,
        user_uuid: UUID,
        role: RoleType = "member",
    ) -> None:
        if session_uuid in self._active_connections:
            self._active_connections[session_uuid][role].pop(
                user_uuid,
                None,
            )

            if (
                not self._active_connections[session_uuid]["member"]
                and not self._active_connections[session_uuid]["host"]
            ):
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
            for role in ["member", "host"]:
                connections = list(
                    self._active_connections[session_uuid][role].values()
                )

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
        role: RoleType = "member",
    ) -> None:
        if session_uuid in self._active_connections:
            for connection in self._active_connections[session_uuid][role].values():
                try:
                    await connection.send_json(message)
                except Exception:
                    pass


session_manager = SessionConnectionManager()
