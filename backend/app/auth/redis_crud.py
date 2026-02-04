from redis.asyncio import Redis

BLACKLIST_PREFIX = "blacklist:token:access:"


async def blacklist_access_token(token: str, ttl: int, redis_client: Redis) -> bool:
    key = f"{BLACKLIST_PREFIX}{token}"
    result = await redis_client.set(
        name=key,
        value=1,
        ex=ttl,
        nx=True,
    )

    return result is not None


async def is_access_token_blacklisted(token: str, redis_client: Redis) -> bool:
    key = f"{BLACKLIST_PREFIX}{token}"
    value = await redis_client.get(name=key)

    return value is not None
