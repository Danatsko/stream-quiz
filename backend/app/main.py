from contextlib import asynccontextmanager
from typing import AsyncGenerator, Any

from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, Any]:
    yield


app = FastAPI(lifespan=lifespan)
