import redis.asyncio as redis_asyncio

from app.core.config import settings

_pool = redis_asyncio.ConnectionPool.from_url(
    settings.redis.url,
    decode_responses=True,
    protocol=3,
)
_client = redis_asyncio.Redis(connection_pool=_pool)


async def get_redis_client() -> redis_asyncio.Redis:
    return _client


async def close_redis_connection() -> None:
    await _client.aclose()
    await _pool.aclose()
