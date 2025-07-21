# SSL证书配置脚本 (PowerShell版本)
# 用于在Windows环境下配置Let's Encrypt SSL证书

Write-Host "开始配置SSL证书..." -ForegroundColor Green

# 设置工作目录
Set-Location $PSScriptRoot\..

# 检查docker-compose是否可用
try {
    docker-compose --version | Out-Null
    Write-Host "Docker Compose 检查通过" -ForegroundColor Green
} catch {
    Write-Host "错误: Docker Compose 不可用，请确保Docker已安装并运行" -ForegroundColor Red
    exit 1
}

# 检查Nginx容器是否运行
$nginxStatus = docker-compose ps nginx --format json | ConvertFrom-Json
if ($nginxStatus.State -ne "running") {
    Write-Host "启动Nginx容器..." -ForegroundColor Yellow
    docker-compose up -d nginx
    Start-Sleep -Seconds 5
}

# 检查Nginx配置语法
Write-Host "检查Nginx配置语法..." -ForegroundColor Yellow
$configTest = docker-compose exec nginx nginx -t 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "Nginx配置语法检查通过" -ForegroundColor Green
} else {
    Write-Host "错误: Nginx配置语法错误" -ForegroundColor Red
    Write-Host $configTest -ForegroundColor Red
    exit 1
}

# 重新加载Nginx配置
Write-Host "重新加载Nginx配置..." -ForegroundColor Yellow
$reloadResult = docker-compose exec nginx nginx -s reload 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ SSL配置成功！" -ForegroundColor Green
    Write-Host ""
    Write-Host "现在可以通过以下地址访问:" -ForegroundColor Cyan
    Write-Host "  - https://xinguang.online" -ForegroundColor White
    Write-Host "  - https://www.xinguang.online" -ForegroundColor White
    Write-Host "  - HTTP请求将自动重定向到HTTPS" -ForegroundColor White
} else {
    Write-Host "❌ Nginx重新加载失败" -ForegroundColor Red
    Write-Host $reloadResult -ForegroundColor Red
    exit 1
}

# 显示服务状态
Write-Host ""
Write-Host "服务状态:" -ForegroundColor Cyan
docker-compose ps

Write-Host ""
Write-Host "🔒 SSL配置完成！网站现在支持HTTPS访问。" -ForegroundColor Green
Write-Host ""
Write-Host "注意事项:" -ForegroundColor Yellow
Write-Host "1. 确保服务器上的证书文件路径正确: /etc/letsencrypt/live/xinguang.online/" -ForegroundColor White
Write-Host "2. 证书将在到期前自动续期（如果配置了自动续期）" -ForegroundColor White
Write-Host "3. 可以使用 'docker-compose logs nginx' 查看Nginx日志" -ForegroundColor White