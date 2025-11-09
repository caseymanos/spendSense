# Dockerfile for FastAPI backend deployment
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
RUN uv sync --frozen --no-cache

# Copy application code
COPY api ./api
COPY features ./features
COPY guardrails ./guardrails
COPY ingest ./ingest
COPY personas ./personas
COPY recommend ./recommend
COPY scripts ./scripts
COPY data ./data

# Expose port
EXPOSE 8000

# Run database seeding and start server
CMD ["sh", "-c", "uv run python scripts/seed_educational_videos.py && uv run uvicorn api.main:app --host 0.0.0.0 --port 8000"]
