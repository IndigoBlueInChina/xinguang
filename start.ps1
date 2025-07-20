# 易和书院多服务平台 - 快速启动脚本
# 一键启动所有服务

Write-Host "=== 易和书院多服务平台 - 快速启动 ===" -ForegroundColor Green
Write-Host ""

# 检查Docker环境
try {
    $dockerVersion = docker --version
    $composeVersion = docker-compose --version
    Write-Host "✓ Docker环境检查通过" -ForegroundColor Green
}
catch {
    Write-Host "✗ Docker环境检查失败，请确保Docker已安装并启动" -ForegroundColor Red
    exit 1
}

# 检查.env文件
if (-not (Test-Path ".env")) {
    Write-Host "⚠ 未找到.env文件，正在创建..." -ForegroundColor Yellow
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "✓ 已创建.env文件" -ForegroundColor Green
    }
}

# 创建数据目录
$directories = @(
    "data\speech-to-text\models",
    "data\speech-to-text\uploads",
    "data\speech-to-text\logs"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "✓ 创建目录: $dir" -ForegroundColor Green
    }
}

# 启动服务
Write-Host ""
Write-Host "正在启动服务..." -ForegroundColor Blue
try {
    docker-compose up -d speech-to-text nginx
    
    Write-Host ""
    Write-Host "✓ 服务启动成功！" -ForegroundColor Green
    Write-Host ""
    Write-Host "=== 服务访问地址 ===" -ForegroundColor Cyan
    Write-Host "语音转文字API文档: http://localhost/api/speech-to-text/docs" -ForegroundColor White
    Write-Host "健康检查: http://localhost/health" -ForegroundColor White
    Write-Host ""
    Write-Host "=== 常用命令 ===" -ForegroundColor Cyan
    Write-Host "查看服务状态: docker-compose ps" -ForegroundColor White
    Write-Host "查看日志: docker-compose logs -f" -ForegroundColor White
    Write-Host "停止服务: docker-compose down" -ForegroundColor White
    Write-Host ""
    Write-Host "如需启动Jitsi会议系统，请进入services/jitsi目录并配置.env文件" -ForegroundColor Yellow
}
catch {
    Write-Host "✗ 服务启动失败: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}