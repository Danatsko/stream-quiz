import uuid
from typing import Annotated, Any

import jwt
from fastapi import Cookie, HTTPException, status, Depends
from redis.asyncio import Redis

from app.auth.redis_crud import is_access_token_blacklisted
from app.core.config import settings
from app.core.redis import get_redis_client


async def get_optional_auth_context(
    redis_client: Annotated[Redis, Depends(get_redis_client)],
    access_token: Annotated[str | None, Cookie()] = None,
) -> dict[str, Any] | None:
    if access_token is None:
        return None

    is_blacklisted = await is_access_token_blacklisted(
        token=access_token,
        redis_client=redis_client,
    )

    if is_blacklisted:
        return None

    try:
        payload = jwt.decode(
            jwt=access_token,
            key=settings.auth.jwt_secret_key.get_secret_value(),
            algorithms=[settings.auth.jwt_algorithm],
        )

        return {
            "access_token": access_token,
            "user_uuid": uuid.UUID(payload["user_uuid"]),
        }
    except (jwt.ExpiredSignatureError, jwt.PyJWTError):
        return None


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
