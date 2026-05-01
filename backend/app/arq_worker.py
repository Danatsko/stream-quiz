from typing import Any

from arq.connections import RedisSettings

from app.core.config import settings
from app.core.db import close_db_connection, init_db
from app.core.redis import close_redis_connection, init_redis
from app.auth.arq_tasks import send_verification_email
from app.sessions.arq_tasks import auto_close_session


async def startup(ctx: dict[str, Any]) -> None:
    await init_db()
    await init_redis()


async def shutdown(ctx: dict[str, Any]) -> None:
    await close_db_connection()
    await close_redis_connection()


class WorkerSettings:
    functions = [
        auto_close_session,
        send_verification_email,
    ]
    redis_settings = RedisSettings.from_dsn(settings.redis.url)
    on_startup = startup
    on_shutdown = shutdown
    max_jobs = 1_000
    job_timeout = 777_600
