import asyncio
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import AsyncGenerator, Any

from fastapi import FastAPI, status, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from redis.asyncio import Redis
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.health import perform_check
from app.core.limiter import limiter
from app.core.db import get_db_session, close_db_connection
from app.core.redis import get_redis_client, close_redis_connection
from app.core.schemas import HealthResponse


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, Any]:
    yield

    await close_db_connection()
    await close_redis_connection()


app = FastAPI(lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(
    "/health",
    status_code=status.HTTP_200_OK,
    response_model=HealthResponse,
)
@limiter.limit("300/minute")
async def health(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    redis_client: Redis = Depends(get_redis_client),
) -> HealthResponse:
    checks_registry = {
        "database": lambda: session.execute(text("SELECT 1")),
        "redis": lambda: redis_client.ping(),
    }
    start_time = time.perf_counter()
    results = await asyncio.gather(
        *[perform_check(func) for func in checks_registry.values()]
    )
    response_time_ms = (time.perf_counter() - start_time) * 1_000
    components_status = dict(zip(checks_registry.keys(), results))
    all_healthy = all(comp["status"] for comp in components_status.values())
    response_data = HealthResponse(
        status="healthy" if all_healthy else "unhealthy",
        components=components_status,
        response_time_ms=response_time_ms,
        timestamp=datetime.now(tz=timezone.utc),
    )

    if not all_healthy:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=response_data.model_dump(mode="json"),
        )

    return response_data
