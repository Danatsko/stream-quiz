from redis.asyncio import ConnectionPool, Redis

from app.core.config import settings

_pool: ConnectionPool | None = None
_client: Redis | None = None


async def init_redis() -> None:
    global _pool, _client

    _pool = ConnectionPool.from_url(
        settings.redis.url,
        decode_responses=True,
        protocol=3,
    )
    _client = Redis(connection_pool=_pool)


async def get_redis_client() -> Redis:
    if _client is None:
        raise RuntimeError("Redis client is not initialized")

    return _client


async def close_redis_connection() -> None:
    global _pool, _client

    if _client:
        await _client.aclose()
    if _pool:
        await _pool.aclose()

    _client = None
    _pool = None
