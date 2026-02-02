from typing import Annotated

from fastapi import APIRouter, status, Request, Response, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import ensure_unauthenticated_user
from app.auth.schemas import RegistrationResponse, RegistrationRequest
from app.auth.service import registration as service_registration
from app.core.config import settings
from app.core.db import get_db_session
from app.core.limiter import limiter

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
