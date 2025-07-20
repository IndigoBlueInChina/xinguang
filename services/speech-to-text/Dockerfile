# Single stage build
FROM python:3.11-slim

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

# Install system dependencies (both build and runtime)
RUN apt-get update && apt-get install -y \
    gcc \
    libc6-dev \
    curl \
    build-essential \
    git \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# 安装指定版本的 Poetry
RUN pip install poetry==${POETRY_VERSION}

# Set working directory and copy project files
WORKDIR /app

# Copy Poetry configuration files first for better caching
COPY pyproject.toml poetry.lock* ./

# Install dependencies
RUN poetry --version && poetry install --only main --no-root --no-interaction

# Copy the rest of the application
COPY app/ ./app/
COPY shared/ ./shared/

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