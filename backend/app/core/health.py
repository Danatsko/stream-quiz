import asyncio
import time
from typing import Callable, Awaitable, Any


async def perform_check(
    check_func: Callable[[], Awaitable[Any]],
    timeout: float = 5.0,
) -> dict[str, Any]:
    start_time = time.perf_counter()

    try:
        await asyncio.wait_for(
            fut=check_func(),
            timeout=timeout,
        )

        response_time_ms = (time.perf_counter() - start_time) * 1_000

        return {
            "status": True,
            "detail": "connected",
            "response_time_ms": round(
                number=response_time_ms,
                ndigits=2,
            ),
        }
    except Exception as exc:
        response_time_ms = (time.perf_counter() - start_time) * 1_000

        return {
            "status": False,
            "detail": str(exc),
            "response_time_ms": round(
                number=response_time_ms,
                ndigits=2,
            ),
        }
