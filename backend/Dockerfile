# syntax=docker/dockerfile:1.4
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/apps:/app

WORKDIR /app

FROM base AS builder

COPY --from=ghcr.io/astral-sh/uv:0.6.17 /uv /usr/local/bin/uv
COPY requirements.prod.txt /tmp/requirements.txt

ENV UV_COMPILE_BYTECODE=0 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

# /tmp is often a small tmpfs during docker build; pip/uv unpack there and can hit ENOSPC
# even when the host disk (and `docker system df`) looks fine.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=cache,target=/var/tmp/pip \
    mkdir -p /var/tmp/pip \
    && TMPDIR=/var/tmp/pip uv pip install --python /usr/local/bin/python --prefix=/install -r /tmp/requirements.txt \
    && rm -rf /tmp/*

FROM base AS runner

COPY --from=builder /install /usr/local
COPY backend/ /app/

EXPOSE 8000

ENTRYPOINT ["sh", "-c", "alembic upgrade head && exec uvicorn main:app --host 0.0.0.0 --port 8000"]
