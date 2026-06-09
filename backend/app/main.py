import asyncio
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import AsyncGenerator, Any, Annotated

from fastapi import FastAPI, status, Depends, HTTPException, Request, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from redis.asyncio import Redis
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.router import auth_router
from app.core.arq import init_arq_pool, close_arq_pool
from app.core.config import settings
from app.core.exception_handlers import (
    not_found_handler,
    conflict_handler,
    validation_handler,
    unprocessable_entity_handler,
    unauthorized_handler,
    forbidden_handler,
    domain_fallback_handler,
)
from app.core.exceptions import (
    NotFoundError,
    ConflictError,
    ValidationError,
    UnprocessableEntityError,
    NotAuthenticatedError,
    InvalidCredentialsError,
    InvalidTokenError,
    AccountNotVerifiedError,
    AlreadyAuthenticatedError,
    DomainException,
)
from app.core.health import perform_check
from app.core.limiter import limiter
from app.core.db import get_db_session, close_db_connection, init_db
from app.core.redis import get_redis_client, close_redis_connection, init_redis
from app.core.schemas import HealthResponse
from app.sessions.ws_pubsub import (
    global_take_redis_pubsub_listener,
    global_host_redis_pubsub_listener,
)
from app.users.router import users_router
from app.quizzes.router import quizzes_router
from app.rooms.router import rooms_router
from app.sessions.ws_router import sessions_ws_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, Any]:
    await init_db()
    await init_redis()
    await init_arq_pool()

    redis_client = await get_redis_client()
    take_pubsub_task = asyncio.create_task(
        global_take_redis_pubsub_listener(redis_client)
    )
    host_pubsub_task = asyncio.create_task(
        global_host_redis_pubsub_listener(redis_client)
    )

    yield

    take_pubsub_task.cancel()
    host_pubsub_task.cancel()
    await close_arq_pool()
    await close_redis_connection()
    await close_db_connection()


app = FastAPI(
    lifespan=lifespan,
    debug=settings.app.debug,
)
app.state.limiter = limiter
app.add_exception_handler(
    exc_class_or_status_code=RateLimitExceeded,
    handler=_rate_limit_exceeded_handler,
)
app.add_exception_handler(
    exc_class_or_status_code=NotFoundError,
    handler=not_found_handler,
)
app.add_exception_handler(
    exc_class_or_status_code=ConflictError,
    handler=conflict_handler,
)
app.add_exception_handler(
    exc_class_or_status_code=ValidationError,
    handler=validation_handler,
)
app.add_exception_handler(
    exc_class_or_status_code=UnprocessableEntityError,
    handler=unprocessable_entity_handler,
)
app.add_exception_handler(
    exc_class_or_status_code=NotAuthenticatedError,
    handler=unauthorized_handler,
)
app.add_exception_handler(
    exc_class_or_status_code=InvalidCredentialsError,
    handler=unauthorized_handler,
)
app.add_exception_handler(
    exc_class_or_status_code=InvalidTokenError,
    handler=unauthorized_handler,
)
app.add_exception_handler(
    exc_class_or_status_code=AccountNotVerifiedError,
    handler=forbidden_handler,
)
app.add_exception_handler(
    exc_class_or_status_code=AlreadyAuthenticatedError,
    handler=forbidden_handler,
)
app.add_exception_handler(
    exc_class_or_status_code=DomainException,
    handler=domain_fallback_handler,
)
app.add_middleware(middleware_class=SlowAPIMiddleware)
app.add_middleware(
    middleware_class=CORSMiddleware,
    allow_origins=settings.cors.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router_v1 = APIRouter()
ws_router_v1 = APIRouter()

api_router_v1.include_router(
    router=auth_router,
    prefix="/auth",
    tags=["auth"],
)
api_router_v1.include_router(
    router=users_router,
    prefix="/users",
    tags=["users"],
)
api_router_v1.include_router(
    router=quizzes_router,
    prefix="/quizzes",
    tags=["quizzes"],
)
api_router_v1.include_router(
    router=rooms_router,
    prefix="/rooms",
    tags=["rooms"],
)
ws_router_v1.include_router(
    router=sessions_ws_router,
    prefix="/sessions",
    tags=["sessions"],
)
app.include_router(
    router=api_router_v1,
    prefix="/api/v1",
)
app.include_router(
    router=ws_router_v1,
    prefix="/ws/v1",
)


@app.get(
    "/health",
    status_code=status.HTTP_200_OK,
    response_model=HealthResponse,
)
@limiter.limit("300/minute")
async def health(
    request: Request,
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    redis_client: Annotated[Redis, Depends(get_redis_client)],
) -> HealthResponse:
    checks_registry = {
        "database": lambda: db_session.execute(text("SELECT 1")),
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
