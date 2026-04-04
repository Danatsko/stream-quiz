from uuid import UUID
from typing import Annotated, Any

import jwt
from fastapi import (
    Cookie,
    HTTPException,
    status,
    Depends,
    WebSocket,
    WebSocketException,
)
from redis.asyncio import Redis

from app.auth.redis_crud import is_access_token_blacklisted, is_user_blacklisted
from app.core.config import settings
from app.core.redis import get_redis_client


async def get_optional_auth_context(
    redis_client: Annotated[Redis, Depends(get_redis_client)],
    access_token: Annotated[str | None, Cookie(alias="access_token")] = None,
) -> dict[str, Any] | None:
    if access_token is None:
        return None

    try:
        payload = jwt.decode(
            jwt=access_token,
            key=settings.auth.jwt_secret_key.get_secret_value(),
            algorithms=[settings.auth.jwt_algorithm],
        )
        raw_user_uuid = payload.get("sub")
        raw_jti = payload.get("jti")

        if raw_user_uuid is None or raw_jti is None:
            return None

        user_uuid = UUID(raw_user_uuid)
        jti = UUID(raw_jti)
    except (jwt.ExpiredSignatureError, jwt.PyJWTError, ValueError):
        return None

    is_jti_blacklisted = await is_access_token_blacklisted(
        jti=jti,
        redis_client=redis_client,
    )

    if is_jti_blacklisted:
        return None

    is_user_uuid_blacklisted = await is_user_blacklisted(
        user_uuid=user_uuid,
        redis_client=redis_client,
    )

    if is_user_uuid_blacklisted:
        return None

    return {
        "user_uuid": user_uuid,
        "access_token": access_token,
        "payload": payload,
    }


async def get_current_auth_context(
    auth_context: Annotated[dict[str, Any] | None, Depends(get_optional_auth_context)],
) -> dict[str, Any]:
    if auth_context is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    return auth_context


async def ensure_unauthenticated_user(
    auth_context: Annotated[dict[str, Any] | None, Depends(get_optional_auth_context)],
) -> None:
    if auth_context is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Already authenticated",
        )


async def get_current_refresh_token(
    refresh_token: Annotated[str | None, Cookie(alias="refresh_token")] = None,
) -> str:
    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token required",
        )

    return refresh_token


async def get_ws_auth_context(
    websocket: WebSocket,
    redis_client: Annotated[Redis, Depends(get_redis_client)],
) -> dict[str, Any]:
    access_token = websocket.cookies.get("access_token")

    if not access_token:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Missing access token",
        )

    try:
        payload = jwt.decode(
            jwt=access_token,
            key=settings.auth.jwt_secret_key.get_secret_value(),
            algorithms=[settings.auth.jwt_algorithm],
        )
        raw_user_uuid = payload.get("sub")
        raw_jti = payload.get("jti")

        if raw_user_uuid is None or raw_jti is None:
            raise WebSocketException(
                code=status.WS_1008_POLICY_VIOLATION,
                reason="Invalid token payload",
            )

        user_uuid = UUID(raw_user_uuid)
        jti = UUID(raw_jti)
    except (jwt.ExpiredSignatureError, jwt.PyJWTError, ValueError):
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Invalid or expired token",
        )

    is_jti_blacklisted = await is_access_token_blacklisted(
        jti=jti,
        redis_client=redis_client,
    )

    if is_jti_blacklisted:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Token is blacklisted",
        )

    is_user_uuid_blacklisted = await is_user_blacklisted(
        user_uuid=user_uuid,
        redis_client=redis_client,
    )

    if is_user_uuid_blacklisted:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="User is blacklisted",
        )

    return {
        "user_uuid": user_uuid,
        "access_token": access_token,
        "payload": payload,
    }
