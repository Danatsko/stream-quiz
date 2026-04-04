from datetime import datetime, timezone, timedelta
import json
from typing import Any
from uuid import UUID

from redis.asyncio import Redis


async def get_session_info_key(uuid: UUID) -> str:
    key = f"session:{str(uuid)}:info"

    return key


async def get_user_answers_key(
    session_uuid: UUID,
    user_uuid: UUID,
) -> str:
    key = f"session:{session_uuid}:answers:{user_uuid}"

    return key


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
    key = await get_session_info_key(uuid=session_uuid)
    value = await redis_client.set(
        name=key,
        value=json.dumps(redis_session_info),
        ex=ttl,
    )

    return value is not None


async def get_session_info(
    session_uuid: UUID,
    redis_client: Redis,
) -> dict[str, Any]:
    key = await get_session_info_key(uuid=session_uuid)
    session_info = await redis_client.get(name=key)

    return session_info


async def get_user_answered_question_uuids(
    session_uuid: UUID,
    user_uuid: UUID,
    redis_client: Redis,
) -> list[str]:
    key = await get_user_answers_key(
        session_uuid=session_uuid,
        user_uuid=user_uuid,
    )
    answered_question_uuids = await redis_client.hkeys(name=key)

    return set(answered_question_uuids)


async def save_user_answer(
    session_uuid: UUID,
    user_uuid: UUID,
    question_uuid: UUID,
    answer_data: list[str],
    redis_client: Redis,
) -> bool:
    key = await get_user_answers_key(
        session_uuid=session_uuid,
        user_uuid=user_uuid,
    )
    async with redis_client.pipeline() as pipeline:
        await pipeline.hset(
            name=key,
            key=str(question_uuid),
            value=json.dumps(answer_data),
        )
        await pipeline.expire(
            name=key,
            time=86_400,
            nx=True,
        )

        result = await pipeline.execute()

    return bool(result[0])
