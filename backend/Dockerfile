# =============================================================================
# Backend Dockerfile - FastAPI Application
# =============================================================================
# Multi-stage build for optimized production image
# Base: python:3.13-slim | Package Manager: uv
# Target Size: < 600MB | Security: Non-root user (appuser)
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Builder - Install dependencies with uv
# -----------------------------------------------------------------------------
FROM python:3.13-slim AS builder

# Set working directory
WORKDIR /app

# Install uv package manager
# Using pip to install uv as it's the recommended approach
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency files first (for layer caching)
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
# --frozen: Use exact versions from lock file
# --no-install-project: Don't install the project itself, just dependencies
RUN uv sync --frozen --no-install-project

# -----------------------------------------------------------------------------
# Stage 2: Runtime - Minimal production image
# -----------------------------------------------------------------------------
FROM python:3.13-slim AS runtime

# Set working directory
WORKDIR /app

# Install curl for health checks
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
# UID > 10000 follows Kubernetes best practices
RUN useradd --create-home --uid 10001 appuser

# Copy virtual environment from builder
# Copy virtual environment from builder (with correct ownership)
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv

# Copy application source code
COPY --chown=appuser:appuser app/ /app/app/

# Copy alembic configuration and migrations
COPY --chown=appuser:appuser alembic.ini /app/
COPY --chown=appuser:appuser alembic/ /app/alembic/

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Change ownership not needed anymore
# RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose FastAPI port
EXPOSE 8000

# Health check - verify application is responding
# Checks /health endpoint every 30 seconds
# Allows 10 seconds for startup before first check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start FastAPI with uvicorn
# --host 0.0.0.0: Listen on all interfaces (required for container networking)
# --port 8000: Standard FastAPI port
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
