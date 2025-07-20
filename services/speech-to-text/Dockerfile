# Build stage
FROM python:3.11-slim AS builder

# Set environment variables for better Python and Poetry behavior
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=true \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    POETRY_VERSION=2.1.2

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libc6-dev \
    curl \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# 安装指定版本的 Poetry
RUN pip install poetry==${POETRY_VERSION}

# Set working directory and copy project files
WORKDIR /app

# Copy Poetry configuration files first for better caching
COPY pyproject.toml poetry.lock* ./

# Install dependencies (CPU版本)
RUN poetry --version && poetry install --only main --no-root --no-interaction

# Copy the rest of the application
COPY app/ ./app/
COPY shared/ ./shared/

# Production stage
FROM python:3.11-slim

# Install only runtime dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY --from=builder /app/app ./app
COPY --from=builder /app/shared ./shared

# Set environment variables
ENV PYTHONPATH="/app" \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

# 创建必要的目录
RUN mkdir -p /app/uploads /app/logs /app/models

# 创建非root用户
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]