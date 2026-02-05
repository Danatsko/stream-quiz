import uuid

from redis.asyncio import Redis

BLACKLIST_ACCESS_TOKEN_PREFIX = "blacklist:token:access:"
BLACKLIST_USER_PREFIX = "blacklist:user:"


async def blacklist_access_token(jti: uuid.UUID, ttl: int, redis_client: Redis) -> bool:
    key = f"{BLACKLIST_ACCESS_TOKEN_PREFIX}{str(jti)}"
    result = await redis_client.set(
        name=key,
        value=1,
        ex=ttl,
        nx=True,
    )

    return result is not None


async def is_access_token_blacklisted(jti: uuid.UUID, redis_client: Redis) -> bool:
    key = f"{BLACKLIST_ACCESS_TOKEN_PREFIX}{str(jti)}"
    value = await redis_client.get(name=key)

    return value is not None


async def is_user_blacklisted(user_uuid: uuid.UUID, redis_client: Redis) -> bool:
    key = f"{BLACKLIST_USER_PREFIX}{str(user_uuid)}"
    value = await redis_client.get(name=key)

    return value is not None
