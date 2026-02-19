from datetime import datetime

from sqlalchemy import update, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import RefreshToken


async def create_refresh_token(
    user_id: int,
    token: str,
    expires_at: datetime,
    session: AsyncSession,
) -> RefreshToken:
    refresh_token = RefreshToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at,
    )

    session.add(instance=refresh_token)
    await session.flush()

    return refresh_token


async def get_refresh_token_by_token(
    token: str,
    session: AsyncSession,
) -> RefreshToken | None:
    stmt = select(RefreshToken).where(
        RefreshToken.token == token,
        RefreshToken.is_revoked.is_(False),
    )
    result = await session.scalar(stmt)

    return result


async def revoke_refresh_token_by_token(
    token: str,
    session: AsyncSession,
) -> bool:
    stmt = (
        update(RefreshToken)
        .where(
            RefreshToken.token == token,
            RefreshToken.is_revoked.is_(False),
        )
        .values(is_revoked=True)
    )
    result = await session.execute(stmt)

    return result.rowcount == 1
