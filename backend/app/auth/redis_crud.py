from redis.asyncio import Redis

BLACKLIST_PREFIX = "blacklist:access:"


async def is_access_token_blacklisted(token: str, redis_client: Redis) -> bool:
    key = f"{BLACKLIST_PREFIX}{token}"
    value = await redis_client.get(key)

    return value is not None
