import uuid
from typing import Annotated

import jwt
from fastapi import Cookie, HTTPException, status, Depends
from redis.asyncio import Redis

from app.auth.redis_crud import is_access_token_blacklisted
from app.core.config import settings
from app.core.redis import get_redis_client


async def get_optional_user_uuid(
    redis_client: Annotated[Redis, Depends(get_redis_client)],
    access_token: Annotated[str | None, Cookie()] = None,
) -> uuid.UUID | None:
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

        return uuid.UUID(payload["sub"])
    except (jwt.ExpiredSignatureError, jwt.PyJWTError):
        return None


async def get_current_user_uuid(
    user_uuid: Annotated[uuid.UUID | None, Depends(get_optional_user_uuid)],
) -> uuid.UUID:
    if user_uuid is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    return user_uuid


async def ensure_unauthenticated_user(
    user_uuid: Annotated[uuid.UUID | None, Depends(get_optional_user_uuid)],
) -> None:
    if user_uuid is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Already authenticated",
        )
