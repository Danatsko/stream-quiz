# syntax=docker/dockerfile:1

FROM python:3.14-slim-bookworm AS base

FROM base AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT="/opt/venv"

FROM builder AS development-builder

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

FROM builder AS development

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH="/app" \
    APP_ENVIRONMENT="development"

WORKDIR /app

COPY --link --from=development-builder /opt/venv /opt/venv

COPY --link app/ ./app/

COPY --link run_arq_worker.py .

COPY --link alembic.ini .

EXPOSE 8000

CMD ["fastapi", "dev", "app/main.py", "--host", "0.0.0.0"]

FROM builder AS production-builder

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

FROM base AS production

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH="/app" \
    APP_ENVIRONMENT="production" \
    WEB_CONCURRENCY=5

WORKDIR /app

RUN groupadd --system --gid 1000 appuser && \
    useradd --system --uid 1000 --gid appuser --no-create-home --shell /bin/false appuser

COPY --link --from=production-builder --chown=1000:1000 /opt/venv /opt/venv

COPY --link --chown=1000:1000 app/ ./app/

COPY --link --chown=1000:1000 run_arq_worker.py .

COPY --link --chown=1000:1000 alembic.ini .

USER appuser

EXPOSE 8000

CMD ["fastapi", "run", "app/main.py"]