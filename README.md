# 易和书院多服务平台

基于微服务架构的综合服务平台，包含语音转文字、视频会议等多种服务。

## 服务架构

### 🎯 **语音转文字服务**
- 基于SenseVoice本地模型的高精度语音识别
- 支持多种音频格式和语言识别
- 提供RESTful API接口

### 🎥 **Jitsi会议系统**
- 开源视频会议解决方案
- 支持多人音视频通话
- 无需客户端，浏览器直接访问

### 🌐 **Nginx反向代理**
- 统一入口，路由分发
- 负载均衡和SSL终止
- 安全防护和访问控制

## 技术栈

- Python 3.11
- Poetry 依赖管理
- FastAPI Web框架
- Docker & Docker Compose
- Nginx 反向代理
- 阿里SenseVoice API

## 项目结构

```
yiheshuyuan/
├── services/                    # 微服务目录
│   ├── speech-to-text/         # 语音转文字服务
│   │   ├── app/                # 应用代码
│   │   ├── shared/             # 共享代码
│   │   ├── Dockerfile          # 服务镜像
│   │   ├── pyproject.toml      # Python依赖
│   │   └── README.md           # 服务说明
│   └── jitsi/                  # Jitsi会议系统
│       ├── docker-compose.yml  # Jitsi服务编排
│       ├── .env.example        # 环境配置示例
│       └── README.md           # 服务说明
├── nginx/                      # Nginx反向代理
│   ├── nginx.conf             # 主配置文件
│   └── conf.d/                # 站点配置
├── data/                       # 数据存储目录
│   └── speech-to-text/        # 语音服务数据
│       ├── models/            # 模型文件
│       ├── uploads/           # 上传文件
│       └── logs/              # 日志文件
├── scripts/                   # 部署脚本
├── docker-compose.yml         # 主服务编排
└── README.md                  # 项目说明
```

## 快速开始

### 环境要求

- Docker 20.10+
- Docker Compose 2.0+
- 至少8GB内存（用于SenseVoice模型）

### 1. 克隆项目

```bash
git clone <repository-url>
cd yiheshuyuan
```

### 2. 启动语音转文字服务

```bash
# 启动语音转文字服务
docker-compose up -d speech-to-text nginx

# 查看服务状态
docker-compose ps
```

### 3. 启动Jitsi会议系统（可选）

```bash
# 进入jitsi服务目录
cd services/jitsi

# 配置环境变量
cp .env.example .env
# 编辑.env文件，设置域名等配置

# 启动jitsi服务
docker-compose up -d
```

### 4. 访问服务

- 语音转文字API: http://localhost/api/speech-to-text/docs
- Jitsi会议: http://localhost/jitsi/
- 健康检查: http://localhost/health

## 服务使用说明

### 语音转文字API

```bash
# 上传音频文件进行转录
curl -X POST "http://localhost/api/speech-to-text/transcribe" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your-audio-file.wav"

# 获取系统信息
curl -X GET "http://localhost/api/speech-to-text/info"
```

### Jitsi会议系统

- 直接访问: http://localhost/jitsi/
- 创建会议室: 在首页输入会议室名称
- 邀请参与者: 分享会议室链接

### 健康检查

```bash
curl -X GET "http://localhost/health"
```