FROM python:3.10-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libmariadb-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
RUN mkdir -p app && touch app/__init__.py
RUN pip install uv && uv pip install --system ".[prod]"

COPY entrypoint.sh ./
RUN chmod +x entrypoint.sh

# ── Development stage ────────────────────────────────────────────────────────
FROM base AS development
RUN uv pip install --system ".[dev]"
COPY . .
ENTRYPOINT ["./entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ── Production stage ─────────────────────────────────────────────────────────
FROM base AS production
COPY . .
ENTRYPOINT ["./entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
