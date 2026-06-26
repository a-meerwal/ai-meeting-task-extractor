# Stage 1: Build dependencies
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies (often needed for compiling certain python packages)
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# Build wheels for all dependencies to optimize the final image size
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Stage 2: Final minimal runtime image
FROM python:3.11-slim

# Security Hardening: Create a non-root user
RUN addgroup --gid 1001 appgroup && \
    adduser --uid 1001 --gid 1001 --disabled-password --gecos "" appuser

WORKDIR /app

# Install dependencies from wheels
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache /wheels/* && rm -rf /wheels

# Copy the actual application source code and set ownership
COPY --chown=appuser:appgroup . .

# Switch to the non-root user for security
USER appuser

EXPOSE 8000

# Default command (FastAPI). This is overridden by docker-compose for the Celery worker.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
