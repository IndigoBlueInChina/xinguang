# 使用Python 3.11 slim镜像作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VERSION=1.6.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# 安装Poetry
RUN pip install poetry==$POETRY_VERSION

# 复制Poetry配置文件
COPY pyproject.toml poetry.lock* ./

# 配置Poetry并安装依赖
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-root \
    && rm -rf $POETRY_CACHE_DIR

# 复制应用代码
COPY app/ ./app/
COPY shared/ ./shared/

# 创建必要的目录
RUN mkdir -p /app/uploads /app/logs /app/models

# 设置权限
RUN chmod -R 755 /app

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