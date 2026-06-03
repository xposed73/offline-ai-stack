import os
from typing import Optional
from faster_whisper import WhisperModel
import static_ffmpeg
try:
    import torch
except ImportError:
    torch = None
from app.config.settings import settings
from app.core.logging import logger

class WhisperManager:
    """Manages the lifecycle and execution of the local Whisper Speech-to-Text model."""
    
    def __init__(self) -> None:
        self.model: Optional[WhisperModel] = None
        self.device: Optional[str] = None
        self.compute_type: Optional[str] = None

    def initialize(self) -> None:
        """Loads the Whisper model into memory if not already initialized."""
        if self.model is not None:
            return

        # 1. Initialize ffmpeg path
        try:
            logger.info("Initializing static-ffmpeg...")
            static_ffmpeg.add_paths()
        except Exception as e:
            logger.warning(
                f"Failed to automatically register static-ffmpeg path: {e}. "
                "Ensure standard ffmpeg is installed in system PATH."
            )

        # 2. Determine hardware acceleration
        cuda_available = False
        if torch is not None:
            try:
                cuda_available = torch.cuda.is_available()
            except Exception:
                pass

        if cuda_available:
            self.device = "cuda"
            self.compute_type = "float16"
            logger.info("NVIDIA CUDA detected. Whisper will load with GPU acceleration.")
        else:
            self.device = "cpu"
            self.compute_type = "int8"
            logger.info("No NVIDIA CUDA detected. Whisper will run on CPU (int8 quantized).")

        model_name = settings.WHISPER_MODEL
        storage_dir = str(settings.whisper_path)
        logger.info(f"Loading Whisper model '{model_name}' from storage '{storage_dir}'...")

        try:
            self.model = WhisperModel(
                model_name,
                device=self.device,
                compute_type=self.compute_type,
                download_root=storage_dir
            )
            logger.info(f"Whisper model '{model_name}' loaded successfully on {self.device}.")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise e

    def transcribe(self, audio_path: str, language: Optional[str] = None) -> str:
        """Transcribes the given audio file to text.
        
        Args:
            audio_path: Path to the local audio file to transcribe.
            language: Optional language ISO code to force. If None, auto-detected.
            
        Returns:
            The transcribed text string.
        """
        self.initialize()
        
        if not self.model:
            raise RuntimeError("Whisper model is not initialized.")
            
        logger.info(f"Starting Whisper transcription for file: {audio_path}")
        
        # beam_size = 5 is a good balance between speed and precision
        segments, info = self.model.transcribe(
            audio_path,
            beam_size=5,
            language=language
        )
        
        text_segments = []
        for segment in segments:
            text_segments.append(segment.text)
            
        transcription = "".join(text_segments).strip()
        logger.debug(f"Transcription completed. Language detected: {info.language} (probability: {info.language_probability:.2f})")
        
        return transcription

whisper_manager = WhisperManager()
