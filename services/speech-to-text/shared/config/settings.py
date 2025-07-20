"""应用配置模块"""

from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用基础配置
    app_name: str = Field(default="易和书院录音转文字服务", description="应用名称")
    app_version: str = Field(default="0.1.0", description="应用版本")
    debug: bool = Field(default=False, description="调试模式")
    
    # 服务器配置
    host: str = Field(default="0.0.0.0", description="服务器地址")
    port: int = Field(default=8000, description="服务器端口")
    
    # SenseVoice本地模型配置
    SENSEVOICE_MODEL_DIR: Optional[str] = Field(
        default=None,
        description="SenseVoice模型目录路径，为空则自动下载"
    )
    SENSEVOICE_DEVICE: str = Field(
        default="auto",
        description="推理设备：auto, cpu, cuda, mps"
    )
    SENSEVOICE_BATCH_SIZE: int = Field(
        default=1,
        description="批处理大小"
    )
    SENSEVOICE_QUANTIZE: bool = Field(
        default=True,
        description="是否启用量化以减少内存使用"
    )
    SENSEVOICE_CACHE_DIR: str = Field(
        default="./models",
        description="模型缓存目录"
    )
    
    # 文件存储配置
    upload_dir: str = Field(default="./uploads", description="上传文件目录")
    max_file_size: int = Field(default=1024 * 1024 * 1024, description="最大文件大小(字节)")
    allowed_extensions: list[str] = Field(
        default=["wav", "mp3", "m4a", "flac", "aac", "ogg"],
        description="允许的文件扩展名"
    )
    
    @field_validator('allowed_extensions', mode='before')
    @classmethod
    def parse_allowed_extensions(cls, v):
        """解析允许的文件扩展名，支持逗号分隔的字符串"""
        if isinstance(v, str):
            return [ext.strip() for ext in v.split(',') if ext.strip()]
        return v
    
    # 文件清理配置
    file_cleanup_interval: int = Field(default=3600, description="文件清理间隔(秒)")
    file_retention_time: int = Field(default=1800, description="文件保留时间(秒)")
    
    # 安全配置
    secret_key: str = Field(default="your-super-secret-key-change-this-in-production", description="JWT密钥")
    algorithm: str = Field(default="HS256", description="JWT算法")
    access_token_expire_minutes: int = Field(default=30, description="访问令牌过期时间(分钟)")
    
    # 日志配置
    log_level: str = Field(default="INFO", description="日志级别")
    log_file: Optional[str] = Field(default=None, description="日志文件路径")
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False
    }


# 全局配置实例
settings = Settings()