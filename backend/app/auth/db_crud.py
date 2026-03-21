from datetime import datetime

from sqlalchemy import update, select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import RefreshToken


async def create_refresh_token(
    user_id: int,
    token: str,
    expires_at: datetime,
    db_session: AsyncSession,
) -> RefreshToken:
    stmt = (
        insert(RefreshToken)
        .values(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
        )
        .returning(RefreshToken)
    )
    result = await db_session.scalar(stmt)

    return result


async def get_refresh_token_by_token(
    token: str,
    db_session: AsyncSession,
) -> RefreshToken | None:
    stmt = select(RefreshToken).where(
        RefreshToken.token == token,
        RefreshToken.is_revoked.is_(False),
    )
    result = await db_session.scalar(stmt)

    return result


async def revoke_refresh_token_by_token(
    token: str,
    db_session: AsyncSession,
) -> bool:
    stmt = (
        update(RefreshToken)
        .where(
            RefreshToken.token == token,
            RefreshToken.is_revoked.is_(False),
        )
        .values(is_revoked=True)
    )
    result = await db_session.execute(stmt)

    return result.rowcount == 1
