# Stage 1: Use the official `uv` image.
FROM ghcr.io/astral-sh/uv:latest AS uv_builder

# Stage 2: Your actual application image
FROM python:3.12-slim-bookworm

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY --from=uv_builder /uv /usr/local/bin/uv

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    build-essential \
    libpq-dev \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    netcat-openbsd \
    ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml /app/
RUN uv pip install gunicorn --system && uv pip install . --system

COPY . .

WORKDIR /app/source

RUN python manage.py collectstatic --noinput

COPY entrypoint.sh /app/entrypoint.sh
RUN sed -i 's/\r$//g' /app/entrypoint.sh && chmod +x /app/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]