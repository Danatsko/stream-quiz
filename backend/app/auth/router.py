from uuid import UUID
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
    RegistrationRequest,
    LoginRequest,
)
from app.auth.service import (
    registration as service_registration,
    login as service_login,
    logout as service_logout,
    refresh as service_refresh,
)
from app.core.config import settings
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
) -> None:
    result = await service_registration(
        **registration_data.model_dump(),
        db_session=db_session,
    )

    response.set_cookie(
        key="access_token",
        value=result["access_token"],
        httponly=True,
        secure=(not settings.app.debug),
        samesite="lax",
        max_age=settings.auth.access_token_expire_seconds,
    )
    response.set_cookie(
        key="refresh_token",
        value=result["refresh_token"],
        httponly=True,
        secure=(not settings.app.debug),
        samesite="lax",
        max_age=settings.auth.refresh_token_expire_seconds,
        path=settings.auth.refresh_token_cookie_path,
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
        **login_data.model_dump(),
        db_session=db_session,
    )

    response.set_cookie(
        key="access_token",
        value=result["access_token"],
        httponly=True,
        secure=(not settings.app.debug),
        samesite="lax",
        max_age=settings.auth.access_token_expire_seconds,
    )
    response.set_cookie(
        key="refresh_token",
        value=result["refresh_token"],
        httponly=True,
        secure=(not settings.app.debug),
        samesite="lax",
        max_age=settings.auth.refresh_token_expire_seconds,
        path=settings.auth.refresh_token_cookie_path,
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

    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=(not settings.app.debug),
        samesite="lax",
    )
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=(not settings.app.debug),
        samesite="lax",
        path=settings.auth.refresh_token_cookie_path,
    )


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

    response.set_cookie(
        key="access_token",
        value=result["access_token"],
        httponly=True,
        secure=(not settings.app.debug),
        samesite="lax",
        max_age=settings.auth.access_token_expire_seconds,
    )
