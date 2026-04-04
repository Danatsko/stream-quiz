from uuid import UUID

from redis.asyncio import Redis


async def get_blacklist_access_token_key(jti: UUID) -> str:
    key = f"blacklist:token:access:{str(jti)}"

    return key


async def get_blacklist_user_key(uuid: UUID) -> str:
    key = f"blacklist:user:{str(uuid)}"

    return key


async def blacklist_access_token(
    jti: UUID,
    ttl: int,
    redis_client: Redis,
) -> bool:
    key = await get_blacklist_access_token_key(jti=jti)
    result = await redis_client.set(
        name=key,
        value=1,
        ex=ttl,
        nx=True,
    )

    return result is not None


async def is_access_token_blacklisted(
    jti: UUID,
    redis_client: Redis,
) -> bool:
    key = await get_blacklist_access_token_key(jti=jti)
    value = await redis_client.get(name=key)

    return value is not None


async def is_user_blacklisted(
    user_uuid: UUID,
    redis_client: Redis,
) -> bool:
    key = await get_blacklist_user_key(uuid=user_uuid)
    value = await redis_client.get(name=key)

    return value is not None
