from uuid import UUID, uuid7
import hashlib
import hmac
from datetime import datetime, timezone, timedelta
import secrets
from typing import Any

from arq import ArqRedis
import jwt
from pwdlib import PasswordHash
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.db_repository import (
    create_refresh_token,
    revoke_refresh_token_by_token,
    get_refresh_token_by_token,
    revoke_all_refresh_tokens_by_user_id as db_repository_revoke_all_refresh_tokens_by_user_id,
)
from app.auth.redis_store import (
    blacklist_access_token,
    blacklist_user as redis_store_blacklist_user,
    set_verification_token,
    get_verification_token,
    mark_verification_token_as_used,
)
from app.core.config import settings
from app.core.exceptions import (
    InvalidCredentialsError,
    AccountNotVerifiedError,
    InvalidTokenError,
    AccountAlreadyVerifiedError,
    UserNotFoundError,
)
from app.users.service import (
    create_user,
    get_user_by_email,
    get_user_by_id,
    verify_user_by_uuid,
    get_user_by_uuid,
)

_password_hash = PasswordHash.recommended()


async def _generate_verification_token() -> str:
    token = secrets.token_hex(nbytes=32)

    return token


async def _generate_access_token(user_uuid: UUID) -> str:
    iat = datetime.now(tz=timezone.utc)
    exp = iat + timedelta(seconds=settings.auth.access_token_expire_seconds)
    data_to_encode = {
        "sub": str(user_uuid),
        "jti": str(uuid7()),
        "iat": iat,
        "exp": exp,
    }
    token = jwt.encode(
        payload=data_to_encode,
        key=settings.auth.jwt_secret_key.get_secret_value(),
        algorithm=settings.auth.jwt_algorithm,
    )

    return token


async def _generate_refresh_token() -> str:
    token = secrets.token_hex(nbytes=32)

    return token


async def _pepper_refresh_token(token: str) -> str:
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


async def _hash_password(password: str) -> str:
    password_bytes = password.encode(encoding="utf-8")
    pepper_bytes = settings.auth.password_pepper.get_secret_value().encode(
        encoding="utf-8"
    )
    peppered_password = hmac.new(
        key=pepper_bytes,
        msg=password_bytes,
        digestmod=hashlib.sha256,
    ).hexdigest()
    hashed_password = _password_hash.hash(password=peppered_password)

    return hashed_password


async def _verify_password(
    password: str,
    hashed_password: str,
) -> bool:
    password_bytes = password.encode(encoding="utf-8")
    pepper_bytes = settings.auth.password_pepper.get_secret_value().encode(
        encoding="utf-8"
    )
    peppered_password = hmac.new(
        key=pepper_bytes,
        msg=password_bytes,
        digestmod=hashlib.sha256,
    ).hexdigest()
    is_verified = _password_hash.verify(
        password=peppered_password,
        hash=hashed_password,
    )

    return is_verified


async def blacklist_user(
    user_uuid: UUID,
    redis_client: Redis,
) -> bool:
    is_blacklisted = await redis_store_blacklist_user(
        user_uuid=user_uuid,
        ttl=settings.auth.access_token_expire_seconds,
        redis_client=redis_client,
    )

    return is_blacklisted


async def revoke_all_refresh_tokens_by_user_id(
    user_id: int,
    db_session: AsyncSession,
) -> None:
    await db_repository_revoke_all_refresh_tokens_by_user_id(
        user_id=user_id,
        db_session=db_session,
    )


async def registration(
    username: str,
    email: str,
    password: str,
    db_session: AsyncSession,
    redis_client: Redis,
    arq_pool: ArqRedis,
) -> None:
    hashed_password = await _hash_password(password=password)
    user_db = await create_user(
        username=username,
        email=email,
        password=hashed_password,
        db_session=db_session,
    )
    verification_token = await _generate_verification_token()

    await set_verification_token(
        token=verification_token,
        user_uuid=user_db.uuid,
        ttl=settings.auth.verification_token_expire_seconds,
        redis_client=redis_client,
    )

    await arq_pool.enqueue_job(
        "send_verification_email",
        email=user_db.email,
        token=verification_token,
    )


async def login(
    email: str,
    password: str,
    db_session: AsyncSession,
) -> dict[str, Any]:
    user_db = await get_user_by_email(
        email=email,
        db_session=db_session,
    )

    if user_db is None:
        raise InvalidCredentialsError()

    is_valid_password = await _verify_password(
        password=password,
        hashed_password=user_db.password,
    )

    if not is_valid_password:
        raise InvalidCredentialsError()

    if not user_db.is_verified:
        raise AccountNotVerifiedError()

    access_token = await _generate_access_token(user_uuid=user_db.uuid)
    refresh_token = await _generate_refresh_token()
    peppered_refresh_token = await _pepper_refresh_token(token=refresh_token)
    refresh_token_expires_at = datetime.now(tz=timezone.utc) + timedelta(
        seconds=settings.auth.refresh_token_expire_seconds
    )

    await create_refresh_token(
        user_id=user_db.id,
        token=peppered_refresh_token,
        expires_at=refresh_token_expires_at,
        db_session=db_session,
    )

    result = {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }

    return result


async def logout(
    access_token_jti: UUID | None,
    access_token_exp: int | None,
    refresh_token: str,
    db_session: AsyncSession,
    redis_client: Redis,
) -> None:
    peppered_refresh_token = await _pepper_refresh_token(token=refresh_token)

    await revoke_refresh_token_by_token(
        token=peppered_refresh_token,
        db_session=db_session,
    )

    if access_token_jti is not None:
        current_timestamp = datetime.now(tz=timezone.utc).timestamp()
        ttl = int(access_token_exp - current_timestamp)

        if ttl > 0:
            await blacklist_access_token(
                jti=access_token_jti,
                ttl=ttl,
                redis_client=redis_client,
            )


async def refresh(
    access_token_jti: UUID | None,
    access_token_exp: int | None,
    refresh_token: str,
    db_session: AsyncSession,
    redis_client: Redis,
) -> dict[str, Any]:
    if access_token_jti is not None:
        current_timestamp = datetime.now(tz=timezone.utc).timestamp()
        ttl = int(access_token_exp - current_timestamp)

        if ttl > 0:
            await blacklist_access_token(
                jti=access_token_jti,
                ttl=ttl,
                redis_client=redis_client,
            )

    peppered_refresh_token = await _pepper_refresh_token(token=refresh_token)
    refresh_token_db = await get_refresh_token_by_token(
        token=peppered_refresh_token,
        db_session=db_session,
    )

    if refresh_token_db is None:
        raise InvalidTokenError(message="Invalid or expired refresh token")

    if refresh_token_db.expires_at < datetime.now(tz=timezone.utc):
        await revoke_refresh_token_by_token(
            token=peppered_refresh_token,
            db_session=db_session,
        )

        raise InvalidTokenError(message="Invalid or expired refresh token")

    user_db = await get_user_by_id(
        id=refresh_token_db.user_id,
        db_session=db_session,
    )

    if user_db is None:
        await revoke_refresh_token_by_token(
            token=peppered_refresh_token,
            db_session=db_session,
        )

        raise InvalidTokenError(message="User not found or deleted")

    new_access_token = await _generate_access_token(user_uuid=user_db.uuid)
    result = {
        "access_token": new_access_token,
    }

    return result


async def verify_account(
    token: str,
    db_session: AsyncSession,
    redis_client: Redis,
) -> dict[str, Any]:
    token_value = await get_verification_token(
        token=token,
        redis_client=redis_client,
    )

    if token_value is None:
        raise InvalidTokenError(message="Invalid or expired verification token")

    if token_value == "used":
        raise AccountAlreadyVerifiedError()

    user_uuid = UUID(token_value)
    user_db = await get_user_by_uuid(
        uuid=user_uuid,
        db_session=db_session,
    )

    if user_db is None:
        raise UserNotFoundError()

    is_verified = await verify_user_by_uuid(
        uuid=user_uuid,
        db_session=db_session,
    )

    if not is_verified:
        raise UserNotFoundError()

    await mark_verification_token_as_used(
        token=token,
        redis_client=redis_client,
    )

    access_token = await _generate_access_token(user_uuid=user_db.uuid)
    refresh_token = await _generate_refresh_token()
    peppered_refresh_token = await _pepper_refresh_token(token=refresh_token)
    refresh_token_expires_at = datetime.now(tz=timezone.utc) + timedelta(
        seconds=settings.auth.refresh_token_expire_seconds
    )

    await create_refresh_token(
        user_id=user_db.id,
        token=peppered_refresh_token,
        expires_at=refresh_token_expires_at,
        db_session=db_session,
    )

    result = {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }

    return result


async def resend_verification(
    email: str,
    redis_client: Redis,
    arq_pool: ArqRedis,
    db_session: AsyncSession,
) -> None:
    user_db = await get_user_by_email(
        email=email,
        db_session=db_session,
    )

    if user_db is None:
        return

    if user_db.is_verified:
        raise AccountAlreadyVerifiedError()

    verification_token = await _generate_verification_token()

    await set_verification_token(
        token=verification_token,
        user_uuid=user_db.uuid,
        ttl=settings.auth.verification_token_expire_seconds,
        redis_client=redis_client,
    )

    await arq_pool.enqueue_job(
        "send_verification_email",
        email=user_db.email,
        token=verification_token,
    )
