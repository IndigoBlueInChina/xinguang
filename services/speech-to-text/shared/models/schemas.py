"""数据模型定义"""

from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime


class TranscriptionRequest(BaseModel):
    """转录请求模型"""
    keywords: Optional[str] = Field(None, description="关键词，用逗号分隔")
    language: str = Field(default="zh-CN", description="语言代码")
    enable_punctuation: bool = Field(default=True, description="启用标点符号")
    enable_word_timestamps: bool = Field(default=True, description="启用词级时间戳")
    
    class Config:
        json_schema_extra = {
            "example": {
                "keywords": "会议,讨论,项目",
                "language": "zh-CN",
                "enable_punctuation": True,
                "enable_word_timestamps": True
            }
        }


class TranscriptionResponse(BaseModel):
    """转录响应模型"""
    success: bool = Field(..., description="是否成功")
    task_id: Optional[str] = Field(None, description="任务ID")
    transcription: Optional[str] = Field(None, description="转录文本")
    processing_time: Optional[float] = Field(None, description="处理时间(秒)")
    file_name: Optional[str] = Field(None, description="文件名")
    timestamp: Optional[int] = Field(None, description="时间戳")
    error: Optional[str] = Field(None, description="错误信息")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "task_id": "task_123456",
                "transcription": "这是转录的文本内容",
                "processing_time": 5.2,
                "file_name": "audio.wav",
                "timestamp": 1640995200,
                "error": None
            }
        }


class FileInfo(BaseModel):
    """文件信息模型"""
    name: str = Field(..., description="文件名")
    size: int = Field(..., description="文件大小(字节)")
    extension: str = Field(..., description="文件扩展名")
    created_time: float = Field(..., description="创建时间")
    modified_time: float = Field(..., description="修改时间")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "audio.wav",
                "size": 1024000,
                "extension": "wav",
                "created_time": 1640995200.0,
                "modified_time": 1640995200.0
            }
        }


class UploadResponse(BaseModel):
    """上传响应模型"""
    success: bool = Field(..., description="是否成功")
    file_id: Optional[str] = Field(None, description="文件ID")
    file_info: Optional[FileInfo] = Field(None, description="文件信息")
    message: str = Field(..., description="响应消息")
    error: Optional[str] = Field(None, description="错误信息")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "file_id": "file_123456",
                "file_info": {
                    "name": "audio.wav",
                    "size": 1024000,
                    "extension": "wav",
                    "created_time": 1640995200.0,
                    "modified_time": 1640995200.0
                },
                "message": "文件上传成功",
                "error": None
            }
        }


class TaskStatus(BaseModel):
    """任务状态模型"""
    task_id: str = Field(..., description="任务ID")
    status: str = Field(..., description="任务状态")
    result: Optional[str] = Field(None, description="任务结果")
    created_time: datetime = Field(..., description="创建时间")
    updated_time: datetime = Field(..., description="更新时间")
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "task_123456",
                "status": "completed",
                "result": "转录完成的文本内容",
                "created_time": "2024-01-01T12:00:00",
                "updated_time": "2024-01-01T12:05:00"
            }
        }


class ErrorResponse(BaseModel):
    """错误响应模型"""
    success: bool = Field(default=False, description="是否成功")
    error: str = Field(..., description="错误信息")
    error_code: Optional[str] = Field(None, description="错误代码")
    timestamp: int = Field(..., description="时间戳")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "文件格式不支持",
                "error_code": "INVALID_FILE_FORMAT",
                "timestamp": 1640995200
            }
        }


class HealthResponse(BaseModel):
    """健康检查响应模型"""
    status: str = Field(..., description="服务状态")
    version: str = Field(..., description="服务版本")
    timestamp: int = Field(..., description="时间戳")
    uptime: float = Field(..., description="运行时间(秒)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "0.1.0",
                "timestamp": 1640995200,
                "uptime": 3600.5
            }
        }


class SystemInfo(BaseModel):
    """系统信息模型"""
    app_name: str = Field(..., description="应用名称")
    version: str = Field(..., description="应用版本")
    debug: bool = Field(..., description="调试模式")
    upload_dir: str = Field(..., description="上传目录")
    max_file_size: int = Field(..., description="最大文件大小（字节）")
    allowed_extensions: List[str] = Field(..., description="允许的文件扩展名")
    supported_languages: List[str] = Field(default=[], description="支持的语言")
    model_info: Dict[str, Any] = Field(default={}, description="模型信息")
    device_info: Dict[str, Any] = Field(default={}, description="设备信息")
    
    class Config:
        json_schema_extra = {
            "example": {
                "app_name": "易和书院录音转文字服务",
                "version": "0.1.0",
                "debug": False,
                "upload_dir": "/tmp/uploads",
                "max_file_size": 104857600,
                "allowed_extensions": ["wav", "mp3", "m4a", "flac"],
                "supported_languages": ["zh-CN", "en-US", "ja-JP"],
                "model_info": {"name": "whisper", "version": "1.0"},
                "device_info": {"type": "cpu", "memory": "8GB"}
            }
        }