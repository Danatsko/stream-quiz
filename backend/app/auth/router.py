from uuid import UUID
from typing import Annotated, Any

from arq import ArqRedis
from fastapi import APIRouter, status, Request, Response, Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import (
    get_optional_auth_context,
    ensure_unauthenticated_user,
    get_current_refresh_token,
)
from app.auth.schemas import (
    RegistrationRequest,
    LoginRequest,
    ResendVerificationRequest,
    VerifyRequest,
)
from app.auth.service import (
    registration as service_registration,
    login as service_login,
    logout as service_logout,
    refresh as service_refresh,
    verify_account,
    resend_verification as service_resend_verification,
)
from app.auth.web_utils import set_auth_cookies, clear_auth_cookies
from app.core.arq import get_arq_pool
from app.core.db import get_db_session
from app.core.limiter import limiter
from app.core.redis import get_redis_client

auth_router = APIRouter()


@auth_router.post(
    path="/registration",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(ensure_unauthenticated_user)],
)
@limiter.limit("5/minute")
async def registration(
    request: Request,
    response: Response,
    registration_data: RegistrationRequest,
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    redis_client: Annotated[Redis, Depends(get_redis_client)],
    arq_pool: Annotated[ArqRedis, Depends(get_arq_pool)],
) -> None:
    await service_registration(
        username=registration_data.username,
        email=registration_data.email,
        password=registration_data.password,
        db_session=db_session,
        redis_client=redis_client,
        arq_pool=arq_pool,
    )


@auth_router.post(
    path="/login",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(ensure_unauthenticated_user)],
)
@limiter.limit("5/minute")
async def login(
    request: Request,
    response: Response,
    login_data: LoginRequest,
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
) -> None:
    result = await service_login(
        email=login_data.email,
        password=login_data.password,
        db_session=db_session,
    )

    await set_auth_cookies(
        response=response,
        access_token=result["access_token"],
        refresh_token=result["refresh_token"],
    )


@auth_router.post(
    path="/logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
@limiter.limit("5/minute")
async def logout(
    request: Request,
    response: Response,
    auth_context: Annotated[dict[str, Any] | None, Depends(get_optional_auth_context)],
    refresh_token: Annotated[str, Depends(get_current_refresh_token)],
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    redis_client: Annotated[Redis, Depends(get_redis_client)],
) -> None:
    access_token_jti = None
    access_token_exp = None

    if auth_context is not None:
        access_token_jti = UUID(auth_context["payload"]["jti"])
        access_token_exp = auth_context["payload"]["exp"]

    await service_logout(
        access_token_jti=access_token_jti,
        access_token_exp=access_token_exp,
        refresh_token=refresh_token,
        db_session=db_session,
        redis_client=redis_client,
    )

    await clear_auth_cookies(response=response)


@auth_router.post(
    path="/refresh",
    status_code=status.HTTP_204_NO_CONTENT,
)
@limiter.limit("5/minute")
async def refresh(
    request: Request,
    response: Response,
    auth_context: Annotated[dict[str, Any] | None, Depends(get_optional_auth_context)],
    refresh_token: Annotated[str, Depends(get_current_refresh_token)],
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    redis_client: Annotated[Redis, Depends(get_redis_client)],
) -> None:
    access_token_jti = None
    access_token_exp = None

    if auth_context is not None:
        access_token_jti = UUID(auth_context["payload"]["jti"])
        access_token_exp = auth_context["payload"]["exp"]

    result = await service_refresh(
        access_token_jti=access_token_jti,
        access_token_exp=access_token_exp,
        refresh_token=refresh_token,
        db_session=db_session,
        redis_client=redis_client,
    )

    await set_auth_cookies(
        response=response,
        access_token=result["access_token"],
    )


@auth_router.post(
    path="/verify",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(ensure_unauthenticated_user)],
)
@limiter.limit("5/minute")
async def verify(
    request: Request,
    response: Response,
    verify_data: VerifyRequest,
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    redis_client: Annotated[Redis, Depends(get_redis_client)],
) -> None:
    result = await verify_account(
        token=verify_data.token,
        db_session=db_session,
        redis_client=redis_client,
    )

    await set_auth_cookies(
        response=response,
        access_token=result["access_token"],
        refresh_token=result["refresh_token"],
    )


@auth_router.post(
    path="/resend-verification",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(ensure_unauthenticated_user)],
)
@limiter.limit("5/minute")
async def resend_verification(
    request: Request,
    resend_verification_data: ResendVerificationRequest,
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    redis_client: Annotated[Redis, Depends(get_redis_client)],
    arq_pool: Annotated[ArqRedis, Depends(get_arq_pool)],
) -> None:
    await service_resend_verification(
        email=resend_verification_data.email,
        db_session=db_session,
        redis_client=redis_client,
        arq_pool=arq_pool,
    )
