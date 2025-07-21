"""日志配置模块"""

import sys
from pathlib import Path
from loguru import logger
from shared.config import settings


def setup_logger():
    """配置日志系统"""
    # 移除默认的控制台处理器
    logger.remove()
    
    # 添加控制台输出（带颜色）
    logger.add(
        sys.stderr,
        level=settings.log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True
    )
    
    # 确保日志目录存在
    log_dir = Path("./logs")
    log_dir.mkdir(exist_ok=True)
    
    # 添加应用日志文件（所有级别）
    logger.add(
        log_dir / "app.log",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
        encoding="utf-8"
    )
    
    # 添加错误日志文件（只记录ERROR和CRITICAL）
    logger.add(
        log_dir / "error.log",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}\n{exception}",
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        encoding="utf-8"
    )
    
    # 添加访问日志文件（用于记录API访问）
    logger.add(
        log_dir / "access.log",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {message}",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
        encoding="utf-8",
        filter=lambda record: "ACCESS" in record["extra"]
    )
    
    logger.info(f"日志系统初始化完成，日志级别: {settings.log_level}")
    logger.info(f"日志文件目录: {log_dir.absolute()}")


def get_access_logger():
    """获取访问日志记录器"""
    return logger.bind(ACCESS=True)