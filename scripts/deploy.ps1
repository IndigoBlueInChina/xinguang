# 易和书院多服务平台部署脚本
# PowerShell脚本，用于简化服务部署和管理

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("all", "speech-to-text", "jitsi", "nginx")]
    [string]$Service = "all",
    
    [Parameter(Mandatory=$false)]
    [ValidateSet("start", "stop", "restart", "status", "logs", "build")]
    [string]$Action = "start",
    
    [Parameter(Mandatory=$false)]
    [switch]$Follow = $false
)

# 设置错误处理
$ErrorActionPreference = "Stop"

# 获取脚本目录
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

# 切换到项目根目录
Set-Location $ProjectRoot

Write-Host "=== 易和书院多服务平台部署脚本 ===" -ForegroundColor Green
Write-Host "项目目录: $ProjectRoot" -ForegroundColor Yellow
Write-Host "服务: $Service" -ForegroundColor Yellow
Write-Host "操作: $Action" -ForegroundColor Yellow
Write-Host ""

# 检查Docker和Docker Compose
function Test-DockerEnvironment {
    try {
        $dockerVersion = docker --version
        $composeVersion = docker-compose --version
        Write-Host "✓ Docker: $dockerVersion" -ForegroundColor Green
        Write-Host "✓ Docker Compose: $composeVersion" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "✗ Docker或Docker Compose未安装或未启动" -ForegroundColor Red
        return $false
    }
}

# 检查环境配置
function Test-EnvironmentConfig {
    if (-not (Test-Path ".env")) {
        Write-Host "⚠ 未找到.env文件，正在从.env.example创建..." -ForegroundColor Yellow
        if (Test-Path ".env.example") {
            Copy-Item ".env.example" ".env"
            Write-Host "✓ 已创建.env文件，请根据需要修改配置" -ForegroundColor Green
        } else {
            Write-Host "✗ 未找到.env.example文件" -ForegroundColor Red
            return $false
        }
    }
    return $true
}

# 创建必要的目录
function Initialize-Directories {
    $directories = @(
        "data/speech-to-text/models",
        "data/speech-to-text/uploads",
        "data/speech-to-text/logs",
        "nginx/logs"
    )
    
    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Host "✓ 创建目录: $dir" -ForegroundColor Green
        }
    }
}

# 构建服务
function Build-Services {
    param([string]$ServiceName)
    
    Write-Host "正在构建服务..." -ForegroundColor Blue
    
    if ($ServiceName -eq "all" -or $ServiceName -eq "speech-to-text") {
        Write-Host "构建语音转文字服务..." -ForegroundColor Blue
        docker-compose build speech-to-text
    }
    
    if ($ServiceName -eq "jitsi") {
        Write-Host "Jitsi服务使用预构建镜像，无需构建" -ForegroundColor Yellow
    }
}

# 启动服务
function Start-Services {
    param([string]$ServiceName)
    
    Write-Host "正在启动服务..." -ForegroundColor Blue
    
    switch ($ServiceName) {
        "all" {
            docker-compose up -d
        }
        "speech-to-text" {
            docker-compose up -d speech-to-text nginx
        }
        "jitsi" {
            Set-Location "services/jitsi"
            if (Test-Path ".env") {
                docker-compose up -d
            } else {
                Write-Host "⚠ Jitsi服务需要先配置.env文件" -ForegroundColor Yellow
                Write-Host "请进入services/jitsi目录，复制.env.example为.env并配置" -ForegroundColor Yellow
            }
            Set-Location $ProjectRoot
        }
        "nginx" {
            docker-compose up -d nginx
        }
    }
}

# 停止服务
function Stop-Services {
    param([string]$ServiceName)
    
    Write-Host "正在停止服务..." -ForegroundColor Blue
    
    switch ($ServiceName) {
        "all" {
            docker-compose down
            Set-Location "services/jitsi"
            if (Test-Path "docker-compose.yml") {
                docker-compose down
            }
            Set-Location $ProjectRoot
        }
        "jitsi" {
            Set-Location "services/jitsi"
            docker-compose down
            Set-Location $ProjectRoot
        }
        default {
            docker-compose stop $ServiceName
        }
    }
}

# 重启服务
function Restart-Services {
    param([string]$ServiceName)
    
    Stop-Services $ServiceName
    Start-Sleep -Seconds 2
    Start-Services $ServiceName
}

# 查看服务状态
function Get-ServicesStatus {
    Write-Host "=== 主服务状态 ===" -ForegroundColor Blue
    docker-compose ps
    
    Write-Host ""
    Write-Host "=== Jitsi服务状态 ===" -ForegroundColor Blue
    Set-Location "services/jitsi"
    if (Test-Path "docker-compose.yml") {
        docker-compose ps
    } else {
        Write-Host "Jitsi服务未配置" -ForegroundColor Yellow
    }
    Set-Location $ProjectRoot
}

# 查看日志
function Get-ServicesLogs {
    param([string]$ServiceName, [bool]$FollowLogs)
    
    $followFlag = if ($FollowLogs) { "-f" } else { "" }
    
    switch ($ServiceName) {
        "all" {
            if ($FollowLogs) {
                docker-compose logs -f
            } else {
                docker-compose logs --tail=50
            }
        }
        "jitsi" {
            Set-Location "services/jitsi"
            if ($FollowLogs) {
                docker-compose logs -f
            } else {
                docker-compose logs --tail=50
            }
            Set-Location $ProjectRoot
        }
        default {
            if ($FollowLogs) {
                docker-compose logs -f $ServiceName
            } else {
                docker-compose logs --tail=50 $ServiceName
            }
        }
    }
}

# 主执行逻辑
try {
    # 检查环境
    if (-not (Test-DockerEnvironment)) {
        exit 1
    }
    
    if (-not (Test-EnvironmentConfig)) {
        exit 1
    }
    
    # 初始化目录
    Initialize-Directories
    
    # 执行操作
    switch ($Action) {
        "build" {
            Build-Services $Service
        }
        "start" {
            Start-Services $Service
            Write-Host ""
            Write-Host "=== 服务访问地址 ===" -ForegroundColor Green
            Write-Host "语音转文字API: http://localhost/api/speech-to-text/docs" -ForegroundColor Cyan
            Write-Host "Jitsi会议: http://localhost/jitsi/" -ForegroundColor Cyan
            Write-Host "健康检查: http://localhost/health" -ForegroundColor Cyan
        }
        "stop" {
            Stop-Services $Service
        }
        "restart" {
            Restart-Services $Service
        }
        "status" {
            Get-ServicesStatus
        }
        "logs" {
            Get-ServicesLogs $Service $Follow
        }
    }
    
    Write-Host ""
    Write-Host "✓ 操作完成" -ForegroundColor Green
}
catch {
    Write-Host "✗ 操作失败: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}