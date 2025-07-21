# SSL证书配置指南

本指南说明如何为易和书院语音转文字服务配置Let's Encrypt SSL证书。

## 前提条件

1. 已在服务器上获取了xinguang.online和www.xinguang.online的SSL证书
2. 证书文件位于：`/etc/letsencrypt/live/xinguang.online/`
3. Docker和Docker Compose已安装并运行

## 配置步骤

### 1. 证书文件确认

确保以下文件存在：
```bash
/etc/letsencrypt/live/xinguang.online/fullchain.pem
/etc/letsencrypt/live/xinguang.online/privkey.pem
```

### 2. 配置文件更新

已完成的配置更新：

#### Nginx配置 (`nginx/conf.d/default.conf`)
- ✅ 添加了HTTPS服务器配置
- ✅ 配置了SSL证书路径
- ✅ 设置了HTTP到HTTPS的自动重定向
- ✅ 添加了现代SSL安全配置
- ✅ 配置了安全头

#### Docker Compose配置 (`docker-compose.yml`)
- ✅ 挂载了Let's Encrypt证书目录
- ✅ 开放了443端口用于HTTPS

### 3. 应用配置

#### 在Linux服务器上：
```bash
# 使用提供的脚本
chmod +x scripts/setup_ssl.sh
./scripts/setup_ssl.sh
```

#### 手动执行：
```bash
# 检查配置语法
docker-compose exec nginx nginx -t

# 重新加载配置
docker-compose exec nginx nginx -s reload
```

#### 在Windows开发环境：
```powershell
# 使用PowerShell脚本
.\scripts\setup_ssl.ps1
```

## 访问地址

配置完成后，可以通过以下地址访问：

- **HTTPS**: https://xinguang.online
- **HTTPS**: https://www.xinguang.online
- **HTTP**: http://xinguang.online (自动重定向到HTTPS)
- **HTTP**: http://www.xinguang.online (自动重定向到HTTPS)

## SSL配置详情

### 支持的协议
- TLS 1.2
- TLS 1.3

### 安全特性
- HSTS (HTTP Strict Transport Security)
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- X-XSS-Protection
- Referrer-Policy

### 证书信息
- 颁发机构：Let's Encrypt
- 有效期：90天（支持自动续期）
- 域名：xinguang.online, www.xinguang.online

## 故障排除

### 1. 证书文件不存在
```bash
# 检查证书文件
ls -la /etc/letsencrypt/live/xinguang.online/

# 如果不存在，重新获取证书
certbot certonly --nginx -d xinguang.online -d www.xinguang.online
```

### 2. Nginx配置错误
```bash
# 检查配置语法
docker-compose exec nginx nginx -t

# 查看错误日志
docker-compose logs nginx
```

### 3. 证书权限问题
```bash
# 确保Docker可以访问证书文件
sudo chmod -R 755 /etc/letsencrypt/
sudo chmod -R 644 /etc/letsencrypt/live/xinguang.online/*.pem
```

### 4. 端口占用
```bash
# 检查端口占用
sudo netstat -tlnp | grep :443
sudo netstat -tlnp | grep :80
```

## 证书续期

Let's Encrypt证书有效期为90天，建议设置自动续期：

```bash
# 添加到crontab
0 12 * * * /usr/bin/certbot renew --quiet && docker-compose exec nginx nginx -s reload
```

## 安全建议

1. **定期更新**：保持Docker镜像和系统更新
2. **监控证书**：设置证书到期提醒
3. **备份证书**：定期备份证书文件
4. **访问控制**：确保只有必要的端口对外开放
5. **日志监控**：定期检查访问日志和错误日志

## 验证SSL配置

可以使用以下工具验证SSL配置：

1. **在线工具**：
   - SSL Labs: https://www.ssllabs.com/ssltest/
   - SSL Checker: https://www.sslchecker.com/

2. **命令行工具**：
```bash
# 检查证书信息
openssl s_client -connect xinguang.online:443 -servername xinguang.online

# 检查证书有效期
echo | openssl s_client -connect xinguang.online:443 2>/dev/null | openssl x509 -noout -dates
```

## 支持

如果遇到问题，请检查：
1. Docker容器状态：`docker-compose ps`
2. Nginx日志：`docker-compose logs nginx`
3. 证书文件权限和路径
4. 防火墙设置（确保80和443端口开放）