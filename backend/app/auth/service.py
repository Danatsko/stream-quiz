import uuid
import hashlib
import hmac
from datetime import datetime, timezone, timedelta
import secrets
from typing import Any

from fastapi import HTTPException, status
import jwt
from pwdlib import PasswordHash
from redis.asyncio import Redis
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.db_crud import (
    create_refresh_token,
    revoke_refresh_token_by_token,
    get_refresh_token_by_token,
)
from app.auth.redis_crud import blacklist_access_token
from app.core.config import settings
from app.users import create_user, get_user_by_email, get_user_by_id

password_hash = PasswordHash.recommended()


async def generate_access_token(user_uuid: uuid.UUID) -> str:
    iat = datetime.now(tz=timezone.utc)
    exp = iat + timedelta(seconds=settings.auth.access_token_expire_seconds)
    data_to_encode = {
        "sub": str(user_uuid),
        "iat": iat,
        "exp": exp,
    }
    token = jwt.encode(
        payload=data_to_encode,
        key=settings.auth.jwt_secret_key.get_secret_value(),
        algorithm=settings.auth.jwt_algorithm,
    )

    return token


async def generate_refresh_token() -> str:
    token = secrets.token_hex(nbytes=32)

    return token


async def pepper_refresh_token(token: str) -> str:
    token_bytes = token.encode(encoding="utf-8")
    pepper_bytes = settings.auth.refresh_token_pepper.get_secret_value().encode(
        encoding="utf-8"
    )
    peppered_token = hmac.new(
        key=pepper_bytes,
        msg=token_bytes,
        digestmod=hashlib.sha256,
    ).hexdigest()

    return peppered_token


async def hash_password(password: str) -> str:
    password_bytes = password.encode(encoding="utf-8")
    pepper_bytes = settings.auth.password_pepper.get_secret_value().encode(
        encoding="utf-8"
    )
    peppered_password = hmac.new(
        key=pepper_bytes,
        msg=password_bytes,
        digestmod=hashlib.sha256,
    ).hexdigest()
    hashed_password = password_hash.hash(password=peppered_password)

    return hashed_password


async def verify_password(password: str, hashed_password: str) -> bool:
    password_bytes = password.encode(encoding="utf-8")
    pepper_bytes = settings.auth.password_pepper.get_secret_value().encode(
        encoding="utf-8"
    )
    peppered_password = hmac.new(
        key=pepper_bytes,
        msg=password_bytes,
        digestmod=hashlib.sha256,
    ).hexdigest()
    is_verified = password_hash.verify(
        password=peppered_password,
        hash=hashed_password,
    )

    return is_verified


async def registration(
    username: str, email: str, password: str, session: AsyncSession
) -> dict[str, Any]:
    hashed_password = await hash_password(password=password)
    user_db = await create_user(
        username=username,
        email=email,
        password=hashed_password,
        session=session,
    )
    access_token = await generate_access_token(user_uuid=user_db.uuid)
    refresh_token = await generate_refresh_token()
    peppered_refresh_token = await pepper_refresh_token(token=refresh_token)
    refresh_token_expires_at = datetime.now(tz=timezone.utc) + timedelta(
        seconds=settings.auth.refresh_token_expire_seconds
    )

    try:
        await create_refresh_token(
            user_id=user_db.id,
            token=peppered_refresh_token,
            expires_at=refresh_token_expires_at,
            session=session,
        )
    except IntegrityError as exc:
        msg = str(exc.orig)

        if "Key (id)=" in msg:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Something went wrong",
            )
        elif "Key (token)=" in msg:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Something went wrong",
            )
        else:
            raise exc

    result = {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }

    return result


async def login(email: str, password: str, session: AsyncSession) -> dict[str, Any]:
    user_db = await get_user_by_email(
        email=email,
        session=session,
    )

    if user_db is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials",
        )

    is_valid_password = await verify_password(
        password=password,
        hashed_password=user_db.password,
    )

    if not is_valid_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials",
        )

    access_token = await generate_access_token(user_uuid=user_db.uuid)
    refresh_token = await generate_refresh_token()
    peppered_refresh_token = await pepper_refresh_token(token=refresh_token)
    refresh_token_expires_at = datetime.now(tz=timezone.utc) + timedelta(
        seconds=settings.auth.refresh_token_expire_seconds
    )

    try:
        await create_refresh_token(
            user_id=user_db.id,
            token=peppered_refresh_token,
            expires_at=refresh_token_expires_at,
            session=session,
        )
    except IntegrityError as exc:
        msg = str(exc.orig)

        if "Key (id)=" in msg:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Something went wrong",
            )
        elif "Key (token)=" in msg:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Something went wrong",
            )
        else:
            raise exc

    result = {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }

    return result


async def logout(
    access_token: str | None,
    access_token_exp: int | None,
    refresh_token: str,
    session: AsyncSession,
    redis_client: Redis,
) -> None:
    peppered_refresh_token = await pepper_refresh_token(token=refresh_token)

    await revoke_refresh_token_by_token(
        token=peppered_refresh_token,
        session=session,
    )

    if access_token is not None:
        current_timestamp = datetime.now(tz=timezone.utc).timestamp()
        ttl = int(access_token_exp - current_timestamp)

        if ttl > 0:
            await blacklist_access_token(
                token=access_token,
                ttl=ttl,
                redis_client=redis_client,
            )


async def refresh(
    access_token: str | None,
    access_token_exp: int | None,
    refresh_token: str,
    session: AsyncSession,
    redis_client: Redis,
) -> dict[str, Any]:
    if access_token is not None:
        current_timestamp = datetime.now(tz=timezone.utc).timestamp()
        ttl = int(access_token_exp - current_timestamp)

        if ttl > 0:
            await blacklist_access_token(
                token=access_token,
                ttl=ttl,
                redis_client=redis_client,
            )

    peppered_refresh_token = await pepper_refresh_token(token=refresh_token)
    refresh_token_db = await get_refresh_token_by_token(
        token=peppered_refresh_token,
        session=session,
    )

    if refresh_token_db is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    if refresh_token_db.expires_at < datetime.now(tz=timezone.utc):
        await revoke_refresh_token_by_token(
            token=peppered_refresh_token,
            session=session,
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    user_db = await get_user_by_id(
        id=refresh_token_db.user_id,
        session=session,
    )

    if user_db is None:
        await revoke_refresh_token_by_token(
            token=peppered_refresh_token,
            session=session,
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or deleted"
        )

    new_access_token = await generate_access_token(user_uuid=user_db.uuid)
    result = {
        "access_token": new_access_token,
    }

    return result
