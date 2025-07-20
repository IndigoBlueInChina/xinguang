# 语音转文字服务 (Speech-to-Text Service)

基于SenseVoice本地模型的语音转文字服务，支持多种音频格式和多语言识别。

## 功能特性

- 🎯 **本地模型推理**：使用SenseVoice本地模型，无需依赖外部API
- 🌍 **多语言支持**：支持中文、英文、日文、韩文、粤语等多种语言
- 📁 **多格式支持**：支持WAV、MP3、M4A、FLAC、AAC、OGG、WMA等音频格式
- ⚡ **高性能推理**：支持CPU、CUDA、MPS等多种推理设备
- 🔒 **安全可靠**：文件自动清理、大小限制、类型验证
- 📊 **实时监控**：健康检查、系统信息、处理状态监控
- 🎨 **友好界面**：现代化Web界面，支持拖拽上传

## 快速开始

### 环境要求

- Python 3.11+
- Poetry (依赖管理)
- FFmpeg (音频处理)

### 安装依赖

```bash
# 安装Poetry
curl -sSL https://install.python-poetry.org | python3 -

# 安装项目依赖
poetry install
```

### 配置环境

```bash
# 复制环境配置文件
cp .env.example .env

# 编辑配置文件
vim .env
```

### 启动服务

```bash
# 开发模式
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Docker部署

```bash
# 构建镜像
docker build -t speech-to-text:latest .

# 运行容器
docker run -d \
  --name speech-to-text \
  -p 8000:8000 \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/logs:/app/logs \
  --env-file .env \
  speech-to-text:latest
```

## API文档

服务启动后，访问以下地址查看API文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

### 主要接口

#### 1. 健康检查
```http
GET /health
```

#### 2. 系统信息
```http
GET /info
```

#### 3. 上传音频文件
```http
POST /upload
Content-Type: multipart/form-data

file: <audio_file>
```

#### 4. 转录音频
```http
POST /transcribe
Content-Type: multipart/form-data

file: <audio_file>
keywords: <optional_keywords>
language: <language_code>  # auto, zh, en, ja, ko, yue
```

#### 5. 下载转录文本
```http
GET /download/{text}
```

## 配置说明

### 模型配置

- `SENSEVOICE_MODEL_DIR`: 本地模型路径（可选，留空自动下载）
- `SENSEVOICE_DEVICE`: 推理设备（auto/cpu/cuda/mps）
- `SENSEVOICE_BATCH_SIZE`: 批处理大小
- `SENSEVOICE_QUANTIZE`: 是否启用量化
- `SENSEVOICE_CACHE_DIR`: 模型缓存目录

### 文件配置

- `UPLOAD_DIR`: 上传目录
- `MAX_FILE_SIZE`: 最大文件大小（字节）
- `ALLOWED_EXTENSIONS`: 允许的文件扩展名
- `FILE_CLEANUP_INTERVAL`: 文件清理间隔（小时）
- `FILE_RETENTION_HOURS`: 文件保留时间（小时）

### 安全配置

- `SECRET_KEY`: JWT密钥
- `JWT_ALGORITHM`: JWT算法
- `JWT_EXPIRE_MINUTES`: JWT过期时间

## 支持的语言

| 语言代码 | 语言名称 |
|---------|----------|
| auto    | 自动检测 |
| zh      | 中文     |
| en      | 英文     |
| ja      | 日文     |
| ko      | 韩文     |
| yue     | 粤语     |

## 支持的音频格式

- WAV (推荐)
- MP3
- M4A
- FLAC
- AAC
- OGG
- WMA

## 性能优化

### GPU加速

如果有NVIDIA GPU，可以启用CUDA加速：

```bash
# 安装CUDA版本的PyTorch
poetry add torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# 设置推理设备
SENSEVOICE_DEVICE=cuda
```

### 内存优化

```bash
# 启用量化以减少内存使用
SENSEVOICE_QUANTIZE=true

# 调整批处理大小
SENSEVOICE_BATCH_SIZE=1
```

## 故障排除

### 常见问题

1. **模型下载失败**
   - 检查网络连接
   - 确保有足够的磁盘空间
   - 尝试手动下载模型到指定目录

2. **CUDA不可用**
   - 检查NVIDIA驱动是否正确安装
   - 确认PyTorch CUDA版本与驱动兼容
   - 降级到CPU推理：`SENSEVOICE_DEVICE=cpu`

3. **内存不足**
   - 启用量化：`SENSEVOICE_QUANTIZE=true`
   - 减少批处理大小：`SENSEVOICE_BATCH_SIZE=1`
   - 使用CPU推理：`SENSEVOICE_DEVICE=cpu`

### 日志查看

```bash
# 查看应用日志
tail -f logs/app.log

# 查看错误日志
tail -f logs/error.log
```

## 开发指南

### 项目结构

```
speech-to-text/
├── app/                    # 应用主目录
│   ├── main.py            # FastAPI应用入口
│   ├── static/            # 静态文件
│   └── __init__.py
├── shared/                # 共享模块
│   ├── config/            # 配置管理
│   ├── models/            # 数据模型
│   ├── utils/             # 工具函数
│   └── __init__.py
├── tests/                 # 测试文件
├── uploads/               # 上传目录
├── logs/                  # 日志目录
├── models/                # 模型缓存
├── pyproject.toml         # 项目配置
├── Dockerfile             # Docker配置
├── .env.example           # 环境变量示例
└── README.md              # 项目文档
```

### 代码规范

```bash
# 代码格式化
poetry run black .

# 导入排序
poetry run isort .

# 代码检查
poetry run flake8 .

# 类型检查
poetry run mypy .
```

### 测试

```bash
# 运行测试
poetry run pytest

# 运行测试并生成覆盖率报告
poetry run pytest --cov=app --cov=shared
```

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！