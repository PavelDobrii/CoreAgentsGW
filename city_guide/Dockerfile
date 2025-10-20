# syntax=docker/dockerfile:1.6
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.2

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir "poetry==${POETRY_VERSION}"

WORKDIR /app

COPY pyproject.toml README.md ./
RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-interaction --no-ansi

COPY city_guide ./city_guide

FROM base AS dev
RUN poetry install --with dev --no-interaction --no-ansi

CMD ["uvicorn", "city_guide.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
