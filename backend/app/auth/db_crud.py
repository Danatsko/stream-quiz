from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import RefreshToken


async def create_refresh_token(
    user_id: int, token: str, expires_at: datetime, session: AsyncSession
) -> RefreshToken:
    refresh_token = RefreshToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at,
    )

    session.add(instance=refresh_token)
    await session.flush()

    return refresh_token
