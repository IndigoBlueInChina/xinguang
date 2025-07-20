"""录音转文字应用主模块"""

import time
import asyncio
from pathlib import Path
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from shared.config import settings
from shared.utils import FileManager, SenseVoiceClient
from shared.models import (
    TranscriptionRequest,
    TranscriptionResponse,
    UploadResponse,
    ErrorResponse,
    HealthResponse,
    SystemInfo
)

# 全局变量
file_manager: Optional[FileManager] = None
sensevoice_client: Optional[SenseVoiceClient] = None
scheduler: Optional[AsyncIOScheduler] = None
app_start_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global file_manager, sensevoice_client, scheduler
    
    # 启动时初始化
    logger.info("正在启动录音转文字服务...")
    
    try:
        # 初始化文件管理器
        file_manager = FileManager(
            upload_dir=settings.upload_dir,
            max_file_size=settings.max_file_size,
            allowed_extensions=settings.allowed_extensions
        )
        logger.info("文件管理器初始化成功")
        
        # 初始化SenseVoice本地模型客户端
        sensevoice_client = SenseVoiceClient(
            model_dir=settings.SENSEVOICE_MODEL_DIR,
            device=settings.SENSEVOICE_DEVICE,
            batch_size=settings.SENSEVOICE_BATCH_SIZE,
            quantize=settings.SENSEVOICE_QUANTIZE,
            cache_dir=settings.SENSEVOICE_CACHE_DIR
        )
        logger.info("SenseVoice本地模型客户端初始化成功")
        
        # 初始化定时任务调度器
        scheduler = AsyncIOScheduler()
        
        # 添加文件清理任务
        scheduler.add_job(
            cleanup_files,
            'interval',
            seconds=settings.file_cleanup_interval,
            id='file_cleanup'
        )
        
        scheduler.start()
        logger.info("定时任务调度器启动成功")
        
        logger.info("录音转文字服务启动完成")
        
    except Exception as e:
        logger.error(f"服务启动失败: {str(e)}")
        raise
    
    yield
    
    # 关闭时清理
    logger.info("正在关闭录音转文字服务...")
    
    if scheduler:
        scheduler.shutdown()
        logger.info("定时任务调度器已关闭")
    
    logger.info("录音转文字服务已关闭")


# 创建FastAPI应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="基于阿里SenseVoice的录音转文字服务",
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


async def cleanup_files():
    """清理过期文件的定时任务"""
    if file_manager:
        deleted_count = file_manager.cleanup_old_files(settings.file_retention_time)
        logger.info(f"定时清理完成，删除了 {deleted_count} 个过期文件")


def get_file_manager() -> FileManager:
    """获取文件管理器依赖"""
    if file_manager is None:
        raise HTTPException(status_code=500, detail="文件管理器未初始化")
    return file_manager


def get_sensevoice_client() -> SenseVoiceClient:
    """获取SenseVoice客户端依赖"""
    if sensevoice_client is None:
        raise HTTPException(status_code=500, detail="SenseVoice客户端未初始化")
    return sensevoice_client


@app.get("/", response_class=FileResponse)
async def index():
    """首页"""
    static_dir = Path(__file__).parent / "static"
    index_file = static_dir / "index.html"
    
    if index_file.exists():
        return FileResponse(index_file)
    else:
        return JSONResponse(
            content={
                "message": "欢迎使用易和书院录音转文字服务",
                "version": settings.app_version,
                "docs": "/docs"
            }
        )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查"""
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        timestamp=int(time.time()),
        uptime=time.time() - app_start_time
    )


@app.get("/info", response_model=SystemInfo)
async def system_info():
    """系统信息"""
    # 获取SenseVoice模型信息
    model_info = {}
    device_info = {}
    if sensevoice_client:
        model_info = sensevoice_client.get_model_info()
        device_info = sensevoice_client.get_device_info()
    
    return SystemInfo(
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        upload_dir=str(settings.UPLOAD_DIR),
        max_file_size=settings.MAX_FILE_SIZE,
        allowed_extensions=list(settings.ALLOWED_EXTENSIONS),
        supported_languages=["zh", "en", "ja", "ko", "yue", "auto"],
        model_info=model_info,
        device_info=device_info
    )


@app.post("/upload", response_model=UploadResponse)
async def upload_audio(
    file: UploadFile = File(..., description="音频文件"),
    fm: FileManager = Depends(get_file_manager)
):
    """上传音频文件"""
    try:
        # 读取文件内容
        file_content = await file.read()
        
        # 保存文件
        file_path = await fm.save_upload_file(file_content, file.filename)
        
        if file_path is None:
            raise HTTPException(
                status_code=400,
                detail="文件上传失败，请检查文件格式和大小"
            )
        
        # 获取文件信息
        file_info = fm.get_file_info(file_path)
        
        return UploadResponse(
            success=True,
            file_id=file_path.name,
            file_info=file_info,
            message="文件上传成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"上传文件时发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


@app.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    file: UploadFile = File(..., description="音频文件"),
    keywords: Optional[str] = Form(None, description="关键词，用逗号分隔"),
    language: str = Form(default="zh-CN", description="语言代码"),
    fm: FileManager = Depends(get_file_manager),
    sv_client: SenseVoiceClient = Depends(get_sensevoice_client)
):
    """转录音频文件"""
    file_path = None
    
    try:
        # 读取并保存文件
        file_content = await file.read()
        file_path = await fm.save_upload_file(file_content, file.filename)
        
        if file_path is None:
            raise HTTPException(
                status_code=400,
                detail="文件保存失败，请检查文件格式和大小"
            )
        
        # 转录音频
        result = await sv_client.transcribe_audio(
            file_path=file_path,
            keywords=keywords,
            language=language
        )
        
        return TranscriptionResponse(
            success=True,
            transcription=result.get("transcription", ""),
            task_id=result.get("task_id", ""),
            processing_time=result.get("processing_time", 0.0),
            file_name=file_path.name,
            language=result.get("language", language),
            timestamp=int(time.time())
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"转录音频时发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"转录失败: {str(e)}")
    
    finally:
        # 清理临时文件
        if file_path and file_path.exists():
            fm.delete_file(file_path)


@app.post("/transcribe-stream")
async def transcribe_audio_stream(
    file: UploadFile = File(..., description="音频文件"),
    keywords: Optional[str] = Form(None, description="关键词，用逗号分隔"),
    language: str = Form(default="zh-CN", description="语言代码"),
    chunk_duration: float = Form(default=30.0, description="音频块时长（秒）"),
    fm: FileManager = Depends(get_file_manager),
    sv_client: SenseVoiceClient = Depends(get_sensevoice_client)
):
    """流式转录音频文件"""
    file_path = None
    
    async def generate_stream():
        nonlocal file_path
        try:
            # 读取并保存文件
            file_content = await file.read()
            file_path = await fm.save_upload_file(file_content, file.filename)
            
            if file_path is None:
                yield f"data: {{\"success\": false, \"error\": \"文件保存失败，请检查文件格式和大小\"}}\n\n"
                return
            
            # 流式转录音频
            async for result in sv_client.transcribe_audio_stream(
                file_path=file_path,
                keywords=keywords,
                language=language,
                chunk_duration=chunk_duration
            ):
                import json
                yield f"data: {json.dumps(result, ensure_ascii=False)}\n\n"
                
        except Exception as e:
            import json
            error_result = {
                "success": False,
                "error": f"流式转录失败: {str(e)}",
                "timestamp": int(time.time())
            }
            yield f"data: {json.dumps(error_result, ensure_ascii=False)}\n\n"
        
        finally:
            # 清理临时文件
            if file_path and file_path.exists():
                fm.delete_file(file_path)
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*"
        }
    )


@app.get("/download/{text}", response_class=FileResponse)
async def download_text(text: str):
    """下载转录文本"""
    try:
        # 创建临时文本文件
        temp_dir = Path(settings.upload_dir)
        temp_file = temp_dir / f"transcription_{int(time.time())}.txt"
        
        # 写入文本内容
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(text)
        
        return FileResponse(
            path=temp_file,
            filename=f"转录文本_{int(time.time())}.txt",
            media_type="text/plain"
        )
        
    except Exception as e:
        logger.error(f"下载文本时发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"下载失败: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )