from typing import Annotated, Any

from fastapi import APIRouter, status, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_auth_context
from app.core.db import get_db_session
from app.core.limiter import limiter
from app.users.schemas import GETMeResponse
from app.users.service import get_me as service_get_me

users_router = APIRouter()


@users_router.get(
    path="/me",
    status_code=status.HTTP_200_OK,
    response_model=GETMeResponse,
)
@limiter.limit("300/minute")
async def get_me(
    request: Request,
    auth_context: Annotated[dict[str, Any], Depends(get_current_auth_context)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> GETMeResponse:
    user_uuid = auth_context["user_uuid"]
    result = await service_get_me(
        uuid=user_uuid,
        session=session,
    )

    return GETMeResponse(
        uuid=result["uuid"],
        username=result["username"],
        email=result["email"],
    )
