from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class Base(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore",
    )


class HealthResponse(Base):
    status: str
    components: dict[str, Any]
    response_time_ms: float
    timestamp: datetime
