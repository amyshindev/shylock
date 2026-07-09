FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/apps:/app \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_COMPILE=1

WORKDIR /app

FROM base AS builder

COPY requirements.prod.txt /tmp/requirements.txt
# Use /var/tmp for pip unpack — /tmp tmpfs is tiny on some docker hosts and causes ENOSPC.
RUN mkdir -p /var/tmp/pip \
    && TMPDIR=/var/tmp/pip pip install --no-cache-dir --prefix=/install -r /tmp/requirements.txt \
    && rm -rf /var/tmp/pip /tmp/*

FROM base AS runner

COPY --from=builder /install /usr/local
COPY backend/ /app/

EXPOSE 8000

ENTRYPOINT ["sh", "-c", "alembic upgrade head && exec uvicorn main:app --host 0.0.0.0 --port 8000"]
