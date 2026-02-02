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
