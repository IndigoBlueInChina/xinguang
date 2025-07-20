"""SenseVoice本地模型客户端模块"""

import time
import os
from typing import Optional, Dict, Any, List
from pathlib import Path
from loguru import logger

try:
    from funasr import AutoModel
    from funasr.utils.postprocess_utils import rich_transcription_postprocess
except ImportError:
    logger.warning("FunASR未安装，请运行: pip install funasr")
    AutoModel = None

try:
    import torch
    import torchaudio
    import librosa
    import numpy as np
except ImportError:
    logger.warning("音频处理库未安装，请运行: pip install torch torchaudio librosa")
    torch = None


class SenseVoiceClient:
    """SenseVoice本地模型语音识别客户端"""
    
    def __init__(
        self,
        model_dir: Optional[str] = None,
        device: str = "auto",
        batch_size: int = 1,
        quantize: bool = True,
        cache_dir: str = "./models"
    ):
        self.model_dir = model_dir
        self.device = self._get_device(device)
        self.batch_size = batch_size
        self.quantize = quantize
        self.cache_dir = Path(cache_dir)
        
        if AutoModel is None:
            raise ImportError("FunASR未安装，请运行: pip install funasr")
        
        if torch is None:
            raise ImportError("PyTorch未安装，请运行: pip install torch torchaudio")
        
        # 初始化模型
        self.model = None
        self.vad_model = None
        self._init_models()
    
    def _get_device(self, device: str) -> str:
        """获取推理设备"""
        if device == "auto":
            if torch and torch.cuda.is_available():
                return "cuda"
            elif torch and hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                return "mps"
            else:
                return "cpu"
        return device
    
    def _init_models(self):
        """初始化SenseVoice模型"""
        try:
            # 确保缓存目录存在
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            
            # 初始化SenseVoice模型
            model_name = self.model_dir or "iic/SenseVoiceSmall"
            logger.info(f"正在加载SenseVoice模型: {model_name}")
            
            self.model = AutoModel(
                model=model_name,
                trust_remote_code=True,
                vad_model="fsmn-vad",
                vad_kwargs={"max_single_segment_time": 30000},
                device=self.device
            )
            
            logger.info(f"SenseVoice模型加载成功，设备: {self.device}")
            
        except Exception as e:
            logger.error(f"SenseVoice模型初始化失败: {str(e)}")
            raise
    
    def _load_audio(self, audio_path: Path) -> np.ndarray:
        """加载音频文件"""
        try:
            # 使用librosa加载音频，自动转换为16kHz单声道
            audio, sr = librosa.load(str(audio_path), sr=16000, mono=True)
            return audio
        except Exception as e:
            logger.error(f"音频文件加载失败: {str(e)}")
            raise
    
    def _preprocess_audio(self, audio: np.ndarray) -> np.ndarray:
        """预处理音频数据"""
        try:
            # 归一化音频
            if np.max(np.abs(audio)) > 0:
                audio = audio / np.max(np.abs(audio))
            
            # 确保音频长度至少为0.1秒
            min_length = int(0.1 * 16000)  # 0.1秒 @ 16kHz
            if len(audio) < min_length:
                audio = np.pad(audio, (0, min_length - len(audio)), mode='constant')
            
            return audio
        except Exception as e:
            logger.error(f"音频预处理失败: {str(e)}")
            raise
    
    async def transcribe_audio(
        self,
        file_path: Path,
        keywords: Optional[str] = None,
        language: str = "auto",
        format_type: str = "wav",
        sample_rate: int = 16000
    ) -> Dict[str, Any]:
        """转录音频文件
        
        Args:
            file_path: 音频文件路径
            keywords: 关键词，用逗号分隔（暂不支持）
            language: 语言代码 (auto, zh, en, ja, ko等)
            format_type: 音频格式（暂不使用）
            sample_rate: 采样率（暂不使用）
            
        Returns:
            转录结果字典
        """
        try:
            if self.model is None:
                raise Exception("模型未初始化")
            
            # 加载和预处理音频
            logger.info(f"开始转录音频文件: {file_path.name}")
            audio = self._load_audio(file_path)
            audio = self._preprocess_audio(audio)
            
            # 构建输入参数
            input_data = [str(file_path)]
            
            # 设置语言参数
            lang_map = {
                "auto": "auto",
                "zh": "zh",
                "zh-CN": "zh",
                "en": "en", 
                "ja": "ja",
                "ko": "ko",
                "yue": "yue"
            }
            target_lang = lang_map.get(language, "auto")
            
            # 执行推理
            start_time = time.time()
            results = self.model.generate(
                input=input_data,
                language=target_lang,
                use_itn=True,
                batch_size=self.batch_size
            )
            
            processing_time = time.time() - start_time
            
            # 处理结果
            if not results or len(results) == 0:
                return {
                    "success": True,
                    "transcription": "",
                    "task_id": f"local_{int(time.time())}",
                    "processing_time": processing_time,
                    "file_name": file_path.name,
                    "timestamp": int(time.time())
                }
            
            result = results[0]
            text = result.get("text", "")
            
            logger.info(f"转录完成，耗时: {processing_time:.2f}秒，文本长度: {len(text)}")
            
            return {
                "success": True,
                "transcription": text,
                "task_id": f"local_{int(time.time())}",
                "processing_time": processing_time,
                "file_name": file_path.name,
                "timestamp": int(time.time())
            }
            
        except Exception as e:
            error_msg = f"转录过程中发生错误: {str(e)}"
            logger.error(f"音频转录失败: {file_path.name}, 错误: {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "file_name": file_path.name,
                "timestamp": int(time.time())
            }
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        try:
            return {
                "success": True,
                "model_name": "SenseVoiceSmall",
                "device": self.device,
                "batch_size": self.batch_size,
                "quantize": self.quantize,
                "status": "ready" if self.model is not None else "not_initialized"
            }
        except Exception as e:
            logger.error(f"获取模型信息失败: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def is_model_ready(self) -> bool:
        """检查模型是否已准备就绪"""
        return self.model is not None
    
    def get_supported_languages(self) -> List[str]:
        """获取支持的语言列表"""
        return ["auto", "zh", "en", "ja", "ko", "yue"]
    
    def get_device_info(self) -> Dict[str, Any]:
        """获取设备信息"""
        info = {
            "device": self.device,
            "device_type": "cpu"
        }
        
        if torch:
            if torch.cuda.is_available():
                info["cuda_available"] = True
                info["cuda_device_count"] = torch.cuda.device_count()
                if self.device.startswith("cuda"):
                    info["device_type"] = "cuda"
                    info["cuda_device_name"] = torch.cuda.get_device_name()
            else:
                info["cuda_available"] = False
            
            if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                info["mps_available"] = True
                if self.device == "mps":
                    info["device_type"] = "mps"
            else:
                info["mps_available"] = False
        
        return info