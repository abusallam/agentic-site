# Backend Dockerfile for Production Deployment
FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast Python package management
RUN pip install uv

# Create app directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt* ./
COPY pyproject.toml* ./
COPY uv.lock* ./

# Install dependencies with uv
RUN if [ -f requirements.txt ]; then uv pip install --system -r requirements.txt; fi
RUN if [ -f pyproject.toml ]; then uv pip install --system -e .; fi

# Install additional production dependencies
RUN uv pip install --system \
    fastapi \
    uvicorn \
    gunicorn \
    supabase \
    openai \
    google-generativeai \
    pydantic \
    redis \
    python-multipart \
    python-jose \
    passlib \
    bcrypt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Start the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]