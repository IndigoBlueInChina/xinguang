# Jitsi Meet 会议系统

基于Docker的Jitsi Meet视频会议系统，提供高质量的音视频通话服务。

## 功能特性

- 🎥 **高清视频通话**：支持多人高清视频会议
- 🎤 **音频会议**：高质量音频通话，支持立体声
- 🖥️ **屏幕共享**：支持桌面和应用程序共享
- 💬 **实时聊天**：会议期间文字聊天功能
- 📱 **多平台支持**：Web、iOS、Android全平台支持
- 🔒 **安全可靠**：端到端加密，密码保护
- 🏠 **大厅功能**：会议室等候功能
- 👥 **分组讨论**：支持分组讨论室
- 📹 **会议录制**：支持会议录制和回放
- 🌍 **多语言**：支持多种界面语言
- 🎛️ **音视频控制**：静音、关闭摄像头、音视频审核
- 📊 **会议统计**：实时连接质量和统计信息

## 快速开始

### 环境要求

- Docker 20.10+
- Docker Compose 2.0+
- 至少2GB内存
- 开放端口：80, 443, 8080, 8443, 10000/udp, 4443

### 部署步骤

1. **克隆配置**
```bash
cd services/jitsi
```

2. **配置环境变量**
```bash
# 复制环境配置文件
cp .env.example .env

# 编辑配置文件
vim .env
```

3. **生成安全密钥**
```bash
# 生成随机密钥
./generate-passwords.sh
```

4. **启动服务**
```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

5. **访问服务**
- Web界面: http://localhost:8080
- HTTPS: https://localhost:8443

### 生产环境部署

1. **域名配置**
```bash
# 修改.env文件
JITSI_DOMAIN=meet.yourdomain.com
DOCKER_HOST_ADDRESS=your.server.ip
```

2. **SSL证书**
```bash
# 启用Let's Encrypt
ENABLE_LETSENCRYPT=1
LETSENCRYPT_EMAIL=admin@yourdomain.com
```

3. **防火墙配置**
```bash
# 开放必要端口
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8080/tcp
sudo ufw allow 8443/tcp
sudo ufw allow 10000/udp
sudo ufw allow 4443/tcp
```

## 配置说明

### 基础配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| JITSI_DOMAIN | 服务域名 | meet.localhost |
| DOCKER_HOST_ADDRESS | 服务器IP地址 | 127.0.0.1 |
| TZ | 时区设置 | Asia/Shanghai |

### 功能开关

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| ENABLE_AUTH | 启用认证 | 0 |
| ENABLE_GUESTS | 启用访客模式 | 1 |
| ENABLE_RECORDING | 启用录制 | 0 |
| ENABLE_LOBBY | 启用大厅 | 1 |
| ENABLE_BREAKOUT_ROOMS | 启用分组讨论 | 1 |

### 音视频设置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| START_AUDIO_MUTED | 默认静音人数 | 10 |
| START_VIDEO_MUTED | 默认关闭视频人数 | 10 |
| RESOLUTION | 视频分辨率 | 720 |
| START_BITRATE | 起始比特率 | 800 |

## 服务组件

### Web前端 (jitsi/web)
- 提供Web界面
- 处理用户交互
- 静态资源服务

### Prosody (jitsi/prosody)
- XMPP服务器
- 用户认证
- 消息路由

### Jicofo (jitsi/jicofo)
- 会议焦点组件
- 会议管理
- 媒体会话协调

### JVB (jitsi/jvb)
- 视频桥接服务器
- 媒体流处理
- 负载均衡

## 高级功能

### 用户认证

1. **启用认证**
```bash
ENABLE_AUTH=1
ENABLE_GUESTS=0
```

2. **创建用户**
```bash
# 进入prosody容器
docker-compose exec prosody /bin/bash

# 创建用户
prosodyctl --config /config/prosody.cfg.lua register user auth.meet.localhost password
```

### 会议录制

1. **启用录制**
```bash
ENABLE_RECORDING=1
```

2. **配置Jibri**
```yaml
# 添加到docker-compose.yml
jibri:
  image: jitsi/jibri:stable
  container_name: jitsi-jibri
  # ... 其他配置
```

### 负载均衡

1. **多JVB部署**
```bash
# 启用OCTO
ENABLE_OCTO=1

# 部署多个JVB实例
docker-compose up --scale jvb=3
```

2. **Nginx负载均衡**
```nginx
upstream jitsi_backend {
    server jitsi-web-1:80;
    server jitsi-web-2:80;
    server jitsi-web-3:80;
}
```

## 监控和维护

### 健康检查

```bash
# 检查服务状态
docker-compose ps

# 查看服务日志
docker-compose logs web
docker-compose logs prosody
docker-compose logs jicofo
docker-compose logs jvb
```

### 性能监控

```bash
# 查看资源使用
docker stats

# 查看网络连接
netstat -tulpn | grep :10000
```

### 备份和恢复

```bash
# 备份配置
tar -czf jitsi-backup-$(date +%Y%m%d).tar.gz config/

# 恢复配置
tar -xzf jitsi-backup-20231201.tar.gz
```

## 故障排除

### 常见问题

1. **无法连接会议**
   - 检查防火墙设置
   - 确认端口10000/udp开放
   - 检查DOCKER_HOST_ADDRESS配置

2. **音视频质量差**
   - 调整比特率设置
   - 检查网络带宽
   - 优化服务器性能

3. **服务启动失败**
   - 检查端口占用
   - 查看容器日志
   - 验证配置文件

### 日志分析

```bash
# Web服务日志
docker-compose logs web | grep ERROR

# JVB连接日志
docker-compose logs jvb | grep "Endpoint connected"

# Prosody认证日志
docker-compose logs prosody | grep "authentication"
```

## 安全建议

1. **修改默认密码**
   - 更改所有组件的默认密码
   - 使用强密码策略

2. **启用HTTPS**
   - 配置SSL证书
   - 强制HTTPS重定向

3. **网络安全**
   - 配置防火墙规则
   - 限制访问IP范围
   - 启用DDoS防护

4. **定期更新**
   - 更新Docker镜像
   - 应用安全补丁
   - 监控安全公告

## API集成

### REST API

```bash
# 创建会议室
curl -X POST https://meet.yourdomain.com/api/rooms \
  -H "Content-Type: application/json" \
  -d '{"name": "my-room", "password": "secret"}'

# 获取会议信息
curl https://meet.yourdomain.com/api/rooms/my-room
```

### Webhook集成

```javascript
// 会议事件监听
api.addEventListener('participantJoined', (event) => {
    console.log('用户加入:', event.id);
});

api.addEventListener('participantLeft', (event) => {
    console.log('用户离开:', event.id);
});
```

## 自定义开发

### 界面定制

```css
/* 自定义样式 */
.welcome-page {
    background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
}

.toolbar {
    background-color: #2c3e50;
}
```

### 插件开发

```javascript
// 自定义插件
class CustomPlugin {
    constructor(conference) {
        this.conference = conference;
    }
    
    init() {
        // 插件初始化逻辑
    }
}
```

## 许可证

Apache License 2.0

## 支持

- 官方文档: https://jitsi.github.io/handbook/
- 社区论坛: https://community.jitsi.org/
- GitHub: https://github.com/jitsi/jitsi-meet