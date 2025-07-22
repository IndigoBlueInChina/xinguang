"""文件处理工具模块"""

import os
import time
import aiofiles
from pathlib import Path
from typing import Optional, TYPE_CHECKING
from loguru import logger

if TYPE_CHECKING:
    from fastapi import UploadFile


class FileManager:
    """文件管理器"""
    
    def __init__(self, upload_dir: str, max_file_size: int, allowed_extensions: list[str]):
        self.upload_dir = Path(upload_dir)
        self.max_file_size = max_file_size
        self.allowed_extensions = [ext.lower() for ext in allowed_extensions]
        
        # 确保上传目录存在
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    def is_allowed_file(self, filename: str) -> bool:
        """检查文件扩展名是否允许"""
        if '.' not in filename:
            return False
        
        extension = filename.rsplit('.', 1)[1].lower()
        return extension in self.allowed_extensions
    
    def get_file_size(self, file_path: Path) -> int:
        """获取文件大小"""
        try:
            return file_path.stat().st_size
        except OSError:
            return 0
    
    def is_file_size_valid(self, file_size: int) -> bool:
        """检查文件大小是否有效"""
        return 0 < file_size <= self.max_file_size
    
    async def save_upload_file(self, file_content: bytes, filename: str) -> Optional[Path]:
        """保存上传的文件"""
        try:
            # 检查文件扩展名
            if not self.is_allowed_file(filename):
                logger.warning(f"不允许的文件类型: {filename}")
                return None
            
            # 检查文件大小
            if not self.is_file_size_valid(len(file_content)):
                logger.warning(f"文件大小超出限制: {filename}, 大小: {len(file_content)}")
                return None
            
            # 生成唯一文件名
            timestamp = int(time.time() * 1000)
            safe_filename = f"{timestamp}_{filename}"
            file_path = self.upload_dir / safe_filename
            
            # 保存文件
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(file_content)
            
            logger.info(f"文件保存成功: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"保存文件失败: {filename}, 错误: {str(e)}")
            return None
    
    async def save_upload_file_stream(self, file: "UploadFile", filename: str) -> Optional[Path]:
        """流式保存上传的文件"""
        try:
            # 检查文件扩展名
            if not self.is_allowed_file(filename):
                logger.warning(f"不允许的文件类型: {filename}")
                return None
            
            # 生成唯一文件名
            timestamp = int(time.time() * 1000)
            safe_filename = f"{timestamp}_{filename}"
            file_path = self.upload_dir / safe_filename
            
            logger.info(f"开始流式接收文件: {filename} -> {safe_filename}")
            
            # 流式保存文件
            total_size = 0
            chunk_count = 0
            chunk_size = 8192  # 8KB chunks
            last_log_size = 0
            log_interval = 1024 * 1024  # 每1MB输出一次日志
            
            async with aiofiles.open(file_path, 'wb') as f:
                while True:
                    chunk = await file.read(chunk_size)
                    if not chunk:
                        logger.info(f"文件接收完成，共接收 {chunk_count} 个数据块")
                        break
                    
                    chunk_count += 1
                    total_size += len(chunk)
                    
                    # 检查文件大小限制
                    if total_size > self.max_file_size:
                        # 删除已写入的部分文件
                        await f.close()
                        if file_path.exists():
                            file_path.unlink()
                        logger.warning(f"文件大小超出限制: {filename}, 大小: {total_size} 字节")
                        return None
                    
                    await f.write(chunk)
                    
                    # 定期输出进度日志
                    if total_size - last_log_size >= log_interval:
                        progress_mb = total_size / (1024 * 1024)
                        logger.info(f"流式接收进度: {progress_mb:.1f}MB ({chunk_count} 块)")
                        last_log_size = total_size
            
            final_size_mb = total_size / (1024 * 1024)
            logger.info(f"流式文件保存成功: {file_path}")
            logger.info(f"文件大小: {total_size} 字节 ({final_size_mb:.2f}MB), 共 {chunk_count} 个数据块")
            return file_path
            
        except Exception as e:
            logger.error(f"流式保存文件失败: {filename}, 错误: {str(e)}")
            # 清理可能的部分文件
            if 'file_path' in locals() and file_path.exists():
                try:
                    file_path.unlink()
                    logger.info(f"已清理部分文件: {file_path}")
                except:
                    pass
            return None
    
    def delete_file(self, file_path: Path) -> bool:
        """删除文件"""
        try:
            if file_path.exists():
                file_path.unlink()
                logger.info(f"文件删除成功: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"删除文件失败: {file_path}, 错误: {str(e)}")
            return False
    
    def cleanup_old_files(self, retention_time: int) -> int:
        """清理过期文件"""
        current_time = time.time()
        deleted_count = 0
        
        try:
            for file_path in self.upload_dir.iterdir():
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > retention_time:
                        if self.delete_file(file_path):
                            deleted_count += 1
            
            logger.info(f"清理完成，删除了 {deleted_count} 个过期文件")
            return deleted_count
            
        except Exception as e:
            logger.error(f"清理文件时出错: {str(e)}")
            return deleted_count
    
    def get_file_info(self, file_path: Path) -> dict:
        """获取文件信息"""
        try:
            stat = file_path.stat()
            return {
                "name": file_path.name,
                "size": stat.st_size,
                "created_time": stat.st_ctime,
                "modified_time": stat.st_mtime,
                "extension": file_path.suffix.lower().lstrip('.')
            }
        except Exception as e:
            logger.error(f"获取文件信息失败: {file_path}, 错误: {str(e)}")
            return {}