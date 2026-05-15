from datetime import datetime, timezone, timedelta
import json
from typing import Any
from uuid import UUID

from redis.asyncio import Redis


async def _get_session_info_key(uuid: UUID | str) -> str:
    key = f"session:{str(uuid)}:info"

    return key


async def _get_session_answers_key(uuid: UUID | str) -> str:
    key = f"session:{str(uuid)}:answers"

    return key


async def _get_session_members_key(uuid: UUID | str) -> str:
    key = f"session:{str(uuid)}:members"

    return key


async def _get_user_answers_key(
    session_uuid: UUID | str,
    user_uuid: UUID | str,
) -> str:
    session_answers_key = await _get_session_answers_key(uuid=session_uuid)
    key = f"{session_answers_key}:{user_uuid}"

    return key


async def get_session_completion_lock_key(uuid: UUID | str) -> str:
    key = f"session:{str(uuid)}:lock:completion"

    return key


async def get_session_take_events_channel(uuid: UUID | str) -> str:
    channel = f"session:{str(uuid)}:events"

    return channel


async def get_session_host_events_channel(uuid: UUID | str) -> str:
    channel = f"session:host:{str(uuid)}:events"

    return channel


async def set_session_info(
    room_uuid: UUID,
    session_uuid: UUID,
    time_seconds: int,
    questions_data: list[dict[str, Any]],
    redis_client: Redis,
) -> bool:
    current_time = datetime.now(tz=timezone.utc)
    end_time = current_time + timedelta(seconds=time_seconds)
    redis_session_info = {
        "room_uuid": str(room_uuid),
        "end_time_ts": end_time.timestamp(),
        "time_seconds": time_seconds,
        "questions": questions_data,
    }
    ttl = time_seconds + 300
    key = await _get_session_info_key(uuid=session_uuid)
    value = await redis_client.set(
        name=key,
        value=json.dumps(redis_session_info),
        ex=ttl,
    )

    return value is not None


async def get_session_info(
    session_uuid: UUID,
    redis_client: Redis,
) -> dict[str, str]:
    key = await _get_session_info_key(uuid=session_uuid)
    session_info = await redis_client.get(name=key)

    return session_info


async def clear_session_data(
    session_uuid: UUID,
    redis_client: Redis,
) -> bool:
    session_info_key = await _get_session_info_key(uuid=session_uuid)
    session_members_key = await _get_session_members_key(uuid=session_uuid)
    match_pattern = await _get_user_answers_key(
        session_uuid=session_uuid, user_uuid="*"
    )
    keys = [session_info_key, session_members_key]
    cursor = 0

    while True:
        cursor, partial_keys = await redis_client.scan(
            cursor=cursor,
            match=match_pattern,
            count=100,
        )

        keys.extend(partial_keys)

        if cursor == 0:
            break

    if keys:
        value = await redis_client.delete(*keys)

        return value is not None

    return False


async def set_user_answer(
    session_uuid: UUID,
    user_uuid: UUID,
    question_uuid: UUID,
    answer_data: list[str],
    time_seconds: int,
    redis_client: Redis,
) -> bool:
    key = await _get_user_answers_key(
        session_uuid=session_uuid,
        user_uuid=user_uuid,
    )
    ttl = time_seconds + 300

    async with redis_client.pipeline() as pipeline:
        await pipeline.hset(
            name=key,
            key=str(question_uuid),
            value=json.dumps(answer_data),
        )
        await pipeline.expire(
            name=key,
            time=ttl,
            nx=True,
        )

        result = await pipeline.execute()

    return result is not None


async def get_user_answered_question_uuids(
    session_uuid: UUID,
    user_uuid: UUID,
    redis_client: Redis,
) -> list[str]:
    key = await _get_user_answers_key(
        session_uuid=session_uuid,
        user_uuid=user_uuid,
    )
    answered_question_uuids = await redis_client.hkeys(name=key)

    return set(answered_question_uuids)


async def get_session_answers(
    session_uuid: UUID,
    redis_client: Redis,
) -> dict[str, dict[str, str]]:
    match_pattern = await _get_user_answers_key(
        session_uuid=session_uuid, user_uuid="*"
    )
    keys = []
    cursor = 0

    while True:
        cursor, partial_keys = await redis_client.scan(
            cursor=cursor,
            match=match_pattern,
            count=100,
        )

        keys.extend(partial_keys)

        if cursor == 0:
            break

    result = {}

    for key in keys:
        user_uuid_str = key.split(":")[-1]
        answers = await redis_client.hgetall(name=key)
        result[user_uuid_str] = answers

    return result


async def set_session_member(
    session_uuid: UUID,
    user_uuid: UUID,
    username: str,
    time_seconds: int,
    redis_client: Redis,
) -> bool:
    key = await _get_session_members_key(uuid=session_uuid)
    ttl = time_seconds + 300

    async with redis_client.pipeline() as pipeline:
        await pipeline.hset(
            name=key,
            key=str(user_uuid),
            value=username,
        )
        await pipeline.expire(
            name=key,
            time=ttl,
        )

        result = await pipeline.execute()

    return result is not None


async def get_session_member(
    session_uuid: UUID,
    user_uuid: UUID,
    redis_client: Redis,
) -> str | None:
    key = await _get_session_members_key(uuid=session_uuid)
    username = await redis_client.hget(
        name=key,
        key=str(user_uuid),
    )

    return username


async def get_session_members(
    session_uuid: UUID,
    redis_client: Redis,
) -> dict[str, str]:
    key = await _get_session_members_key(uuid=session_uuid)
    members = await redis_client.hgetall(name=key)

    return members
