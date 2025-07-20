"""文件处理工具模块"""

import os
import time
import aiofiles
from pathlib import Path
from typing import Optional
from loguru import logger


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