#!/bin/bash

# 易和书院多服务平台部署脚本
# Bash脚本，用于简化服务部署和管理

set -e

# 默认参数
SERVICE="all"
ACTION="start"
FOLLOW=false

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 帮助信息
show_help() {
    echo "易和书院多服务平台部署脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -s, --service SERVICE    指定服务 (all|speech-to-text|jitsi|nginx) [默认: all]"
    echo "  -a, --action ACTION      指定操作 (start|stop|restart|status|logs|build) [默认: start]"
    echo "  -f, --follow            跟踪日志输出 (仅用于logs操作)"
    echo "  -h, --help              显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 --service speech-to-text --action start"
    echo "  $0 --service all --action logs --follow"
    echo "  $0 --action build"
}

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -s|--service)
            SERVICE="$2"
            shift 2
            ;;
        -a|--action)
            ACTION="$2"
            shift 2
            ;;
        -f|--follow)
            FOLLOW=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "未知参数: $1"
            show_help
            exit 1
            ;;
    esac
done

# 验证参数
if [[ ! "$SERVICE" =~ ^(all|speech-to-text|jitsi|nginx)$ ]]; then
    echo -e "${RED}错误: 无效的服务名称 '$SERVICE'${NC}"
    exit 1
fi

if [[ ! "$ACTION" =~ ^(start|stop|restart|status|logs|build)$ ]]; then
    echo -e "${RED}错误: 无效的操作 '$ACTION'${NC}"
    exit 1
fi

# 获取脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 切换到项目根目录
cd "$PROJECT_ROOT"

echo -e "${GREEN}=== 易和书院多服务平台部署脚本 ===${NC}"
echo -e "${YELLOW}项目目录: $PROJECT_ROOT${NC}"
echo -e "${YELLOW}服务: $SERVICE${NC}"
echo -e "${YELLOW}操作: $ACTION${NC}"
echo ""

# 检查Docker和Docker Compose
check_docker_environment() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}✗ Docker未安装${NC}"
        return 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}✗ Docker Compose未安装${NC}"
        return 1
    fi
    
    if ! docker info &> /dev/null; then
        echo -e "${RED}✗ Docker服务未启动${NC}"
        return 1
    fi
    
    local docker_version=$(docker --version)
    local compose_version=$(docker-compose --version)
    echo -e "${GREEN}✓ Docker: $docker_version${NC}"
    echo -e "${GREEN}✓ Docker Compose: $compose_version${NC}"
    return 0
}

# 检查环境配置
check_environment_config() {
    if [[ ! -f ".env" ]]; then
        echo -e "${YELLOW}⚠ 未找到.env文件，正在从.env.example创建...${NC}"
        if [[ -f ".env.example" ]]; then
            cp ".env.example" ".env"
            echo -e "${GREEN}✓ 已创建.env文件，请根据需要修改配置${NC}"
        else
            echo -e "${RED}✗ 未找到.env.example文件${NC}"
            return 1
        fi
    fi
    return 0
}

# 创建必要的目录
initialize_directories() {
    local directories=(
        "data/speech-to-text/models"
        "data/speech-to-text/uploads"
        "data/speech-to-text/logs"
        "nginx/logs"
    )
    
    for dir in "${directories[@]}"; do
        if [[ ! -d "$dir" ]]; then
            mkdir -p "$dir"
            echo -e "${GREEN}✓ 创建目录: $dir${NC}"
        fi
    done
}

# 构建服务
build_services() {
    local service_name="$1"
    
    echo -e "${BLUE}正在构建服务...${NC}"
    
    if [[ "$service_name" == "all" || "$service_name" == "speech-to-text" ]]; then
        echo -e "${BLUE}构建语音转文字服务...${NC}"
        docker-compose build speech-to-text
    fi
    
    if [[ "$service_name" == "jitsi" ]]; then
        echo -e "${YELLOW}Jitsi服务使用预构建镜像，无需构建${NC}"
    fi
}

# 启动服务
start_services() {
    local service_name="$1"
    
    echo -e "${BLUE}正在启动服务...${NC}"
    
    case "$service_name" in
        "all")
            docker-compose up -d
            ;;
        "speech-to-text")
            docker-compose up -d speech-to-text nginx
            ;;
        "jitsi")
            cd "services/jitsi"
            if [[ -f ".env" ]]; then
                docker-compose up -d
            else
                echo -e "${YELLOW}⚠ Jitsi服务需要先配置.env文件${NC}"
                echo -e "${YELLOW}请进入services/jitsi目录，复制.env.example为.env并配置${NC}"
            fi
            cd "$PROJECT_ROOT"
            ;;
        "nginx")
            docker-compose up -d nginx
            ;;
    esac
}

# 停止服务
stop_services() {
    local service_name="$1"
    
    echo -e "${BLUE}正在停止服务...${NC}"
    
    case "$service_name" in
        "all")
            docker-compose down
            cd "services/jitsi"
            if [[ -f "docker-compose.yml" ]]; then
                docker-compose down
            fi
            cd "$PROJECT_ROOT"
            ;;
        "jitsi")
            cd "services/jitsi"
            docker-compose down
            cd "$PROJECT_ROOT"
            ;;
        *)
            docker-compose stop "$service_name"
            ;;
    esac
}

# 重启服务
restart_services() {
    local service_name="$1"
    
    stop_services "$service_name"
    sleep 2
    start_services "$service_name"
}

# 查看服务状态
get_services_status() {
    echo -e "${BLUE}=== 主服务状态 ===${NC}"
    docker-compose ps
    
    echo ""
    echo -e "${BLUE}=== Jitsi服务状态 ===${NC}"
    cd "services/jitsi"
    if [[ -f "docker-compose.yml" ]]; then
        docker-compose ps
    else
        echo -e "${YELLOW}Jitsi服务未配置${NC}"
    fi
    cd "$PROJECT_ROOT"
}

# 查看日志
get_services_logs() {
    local service_name="$1"
    local follow_logs="$2"
    
    case "$service_name" in
        "all")
            if [[ "$follow_logs" == "true" ]]; then
                docker-compose logs -f
            else
                docker-compose logs --tail=50
            fi
            ;;
        "jitsi")
            cd "services/jitsi"
            if [[ "$follow_logs" == "true" ]]; then
                docker-compose logs -f
            else
                docker-compose logs --tail=50
            fi
            cd "$PROJECT_ROOT"
            ;;
        *)
            if [[ "$follow_logs" == "true" ]]; then
                docker-compose logs -f "$service_name"
            else
                docker-compose logs --tail=50 "$service_name"
            fi
            ;;
    esac
}

# 主执行逻辑
main() {
    # 检查环境
    if ! check_docker_environment; then
        exit 1
    fi
    
    if ! check_environment_config; then
        exit 1
    fi
    
    # 初始化目录
    initialize_directories
    
    # 执行操作
    case "$ACTION" in
        "build")
            build_services "$SERVICE"
            ;;
        "start")
            start_services "$SERVICE"
            echo ""
            echo -e "${GREEN}=== 服务访问地址 ===${NC}"
            echo -e "${CYAN}语音转文字API: http://localhost/api/speech-to-text/docs${NC}"
            echo -e "${CYAN}Jitsi会议: http://localhost/jitsi/${NC}"
            echo -e "${CYAN}健康检查: http://localhost/health${NC}"
            ;;
        "stop")
            stop_services "$SERVICE"
            ;;
        "restart")
            restart_services "$SERVICE"
            ;;
        "status")
            get_services_status
            ;;
        "logs")
            get_services_logs "$SERVICE" "$FOLLOW"
            ;;
    esac
    
    echo ""
    echo -e "${GREEN}✓ 操作完成${NC}"
}

# 错误处理
trap 'echo -e "${RED}✗ 操作失败${NC}"; exit 1' ERR

# 执行主函数
main