from typing import Annotated, Any

from fastapi import APIRouter, status, Request, Response, Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import (
    get_optional_auth_context,
    ensure_unauthenticated_user,
    get_current_refresh_token,
)
from app.auth.schemas import (
    RegistrationResponse,
    RegistrationRequest,
    LoginResponse,
    LoginRequest,
    LogoutResponse,
)
from app.auth.service import (
    registration as service_registration,
    login as service_login,
    logout as service_logout,
)
from app.core.config import settings
from app.core.db import get_db_session
from app.core.limiter import limiter
from app.core.redis import get_redis_client

auth_router = APIRouter()


@auth_router.post(
    path="/registration",
    status_code=status.HTTP_201_CREATED,
    response_model=RegistrationResponse,
    dependencies=[Depends(ensure_unauthenticated_user)],
)
@limiter.limit("5/minute")
async def registration(
    request: Request,
    response: Response,
    registration_data: RegistrationRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> RegistrationResponse:
    result = await service_registration(
        **registration_data.model_dump(),
        session=session,
    )

    response.set_cookie(
        key="access_token",
        value=result["access_token"],
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=settings.auth.access_token_expire_seconds,
    )
    response.set_cookie(
        key="refresh_token",
        value=result["refresh_token"],
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=settings.auth.refresh_token_expire_seconds,
    )

    return RegistrationResponse()


@auth_router.post(
    path="/login",
    status_code=status.HTTP_200_OK,
    response_model=LoginResponse,
    dependencies=[Depends(ensure_unauthenticated_user)],
)
@limiter.limit("5/minute")
async def login(
    request: Request,
    response: Response,
    login_data: LoginRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> LoginResponse:
    result = await service_login(
        **login_data.model_dump(),
        session=session,
    )

    response.set_cookie(
        key="access_token",
        value=result["access_token"],
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=settings.auth.access_token_expire_seconds,
    )
    response.set_cookie(
        key="refresh_token",
        value=result["refresh_token"],
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=settings.auth.refresh_token_expire_seconds,
    )

    return LoginResponse()


@auth_router.post(
    path="/logout",
    status_code=status.HTTP_200_OK,
    response_model=LogoutResponse,
)
@limiter.limit("5/minute")
async def logout(
    request: Request,
    response: Response,
    auth_context: Annotated[dict[str, Any] | None, Depends(get_optional_auth_context)],
    refresh_token: Annotated[str, Depends(get_current_refresh_token)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    redis_client: Annotated[Redis, Depends(get_redis_client)],
) -> LogoutResponse:
    access_token = None
    access_token_exp = None

    if auth_context is not None:
        access_token = auth_context["access_token"]
        access_token_exp = auth_context["payload"]["exp"]

    await service_logout(
        access_token=access_token,
        access_token_exp=access_token_exp,
        refresh_token=refresh_token,
        session=session,
        redis_client=redis_client,
    )

    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=False,
        samesite="lax",
    )
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=False,
        samesite="lax",
    )

    return LogoutResponse()
