from arq import create_pool, ArqRedis
from arq.connections import RedisSettings

from app.core.config import settings

_arq_pool: ArqRedis | None = None


async def init_arq_pool() -> None:
    global _arq_pool

    redis_settings = RedisSettings.from_dsn(settings.redis.url)
    _arq_pool = await create_pool(redis_settings)


async def get_arq_pool() -> ArqRedis:
    if _arq_pool is None:
        raise RuntimeError("ARQ pool is not initialized")

    return _arq_pool


async def close_arq_pool() -> None:
    global _arq_pool

    if _arq_pool is not None:
        await _arq_pool.close()

        _arq_pool = None
