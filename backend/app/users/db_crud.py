from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.models import User


async def create_user(
    username: str, email: str, password: str, session: AsyncSession
) -> User:
    user = User(
        username=username,
        email=email,
        password=password,
    )

    session.add(instance=user)
    await session.flush()
    await session.refresh(
        instance=user,
        attribute_names=[
            "id",
            "uuid",
        ],
    )

    return user


async def get_user_by_email(email: str, session: AsyncSession) -> User | None:
    stmt = select(User).where(
        User.email == email,
        User.deleted_at.is_(None),
    )
    result = await session.scalar(stmt)

    return result


async def get_user_by_id(id: int, session: AsyncSession) -> User | None:
    stmt = select(User).where(
        User.id == id,
        User.deleted_at.is_(None),
    )
    result = await session.scalar(stmt)

    return result
