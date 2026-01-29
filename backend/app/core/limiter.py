from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings

limiter = Limiter(
    key_func=get_remote_address,
    strategy="sliding-window-counter",
    storage_uri=settings.redis.url,
)
