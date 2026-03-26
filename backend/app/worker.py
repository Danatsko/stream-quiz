from typing import Any

from arq.connections import RedisSettings

from app.core.config import settings
from app.core.db import close_db_connection
from app.core.redis import close_redis_connection
from app.sessions.arq_tasks import auto_close_session


async def startup(ctx: dict[str, Any]) -> None:
    pass


async def shutdown(ctx: dict[str, Any]) -> None:
    await close_db_connection()
    await close_redis_connection()


class WorkerSettings:
    functions = [auto_close_session]
    redis_settings = RedisSettings.from_dsn(settings.redis.url)
    on_startup = startup
    on_shutdown = shutdown
    max_jobs = 1_000
    job_timeout = 777_600
