import os
from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base Directory of the Project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class AppSettings(BaseSettings):
    """Application-wide settings."""
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # FastAPI settings
    APP_LANGUAGE: str = Field(default="en", env="APP_LANGUAGE")
    APP_HOST: str = Field(default="0.0.0.0", env="APP_HOST")
    APP_PORT: int = Field(default=8000, env="APP_PORT")
    DEBUG: bool = Field(default=True, env="DEBUG")

    # Ollama settings
    OLLAMA_HOST: str = Field(default="http://localhost:11434", env="OLLAMA_HOST")
    LLM_MODEL: str = Field(default="tinyllama", env="LLM_MODEL")
    EMBEDDING_MODEL: str = Field(default="nomic-embed-text", env="EMBEDDING_MODEL")

    # Docker network
    DOCKER_NETWORK: str = Field(default="offline-ai-net", env="DOCKER_NETWORK")

    # Qdrant settings
    QDRANT_HOST: str = Field(default="localhost", env="QDRANT_HOST")
    QDRANT_PORT: int = Field(default=6333, env="QDRANT_PORT")
    QDRANT_GRPC_PORT: int = Field(default=6334, env="QDRANT_GRPC_PORT")
    QDRANT_COLLECTION_NAME: str = Field(default="rag_documents", env="QDRANT_COLLECTION_NAME")

    # OpenWebUI, n8n, & XTTS
    OPENWEBUI_PORT: int = Field(default=3000, env="OPENWEBUI_PORT")
    OPENWEBUI_AUTH: bool = Field(default=False, env="OPENWEBUI_AUTH")
    N8N_PORT: int = Field(default=5678, env="N8N_PORT")
    KOKORO_PORT: int = Field(default=8880, env="KOKORO_PORT")
    KOKORO_IMAGE: str = Field(default="ghcr.io/remsky/kokoro-fastapi-cpu:v0.3.0", env="KOKORO_IMAGE")
    KOKORO_VOICE: str = Field(default="af_sky", env="KOKORO_VOICE")
    KOKORO_MODEL: str = Field(default="kokoro", env="KOKORO_MODEL")
    ENABLE_TTS: bool = Field(default=True, env="ENABLE_TTS")

    # Storage paths
    DATA_DIR: str = Field(default="./data", env="DATA_DIR")
    QDRANT_STORAGE_DIR: str = Field(default="./data/qdrant", env="QDRANT_STORAGE_DIR")
    OPENWEBUI_STORAGE_DIR: str = Field(default="./data/openwebui", env="OPENWEBUI_STORAGE_DIR")
    N8N_STORAGE_DIR: str = Field(default="./data/n8n", env="N8N_STORAGE_DIR")
    KOKORO_STORAGE_DIR: str = Field(default="./data/kokoro", env="KOKORO_STORAGE_DIR")
    INGESTION_DIR: str = Field(default="./data/ingest", env="INGESTION_DIR")

    @property
    def data_path(self) -> Path:
        path = Path(self.DATA_DIR)
        return path if path.is_absolute() else (BASE_DIR / path).resolve()

    @property
    def qdrant_path(self) -> Path:
        path = Path(self.QDRANT_STORAGE_DIR)
        return path if path.is_absolute() else (BASE_DIR / path).resolve()

    @property
    def openwebui_path(self) -> Path:
        path = Path(self.OPENWEBUI_STORAGE_DIR)
        return path if path.is_absolute() else (BASE_DIR / path).resolve()

    @property
    def n8n_path(self) -> Path:
        path = Path(self.N8N_STORAGE_DIR)
        return path if path.is_absolute() else (BASE_DIR / path).resolve()

    @property
    def kokoro_path(self) -> Path:
        path = Path(self.KOKORO_STORAGE_DIR)
        return path if path.is_absolute() else (BASE_DIR / path).resolve()

    @property
    def ingest_path(self) -> Path:
        path = Path(self.INGESTION_DIR)
        return path if path.is_absolute() else (BASE_DIR / path).resolve()

    def ensure_directories(self) -> None:
        """Create necessary data storage directories if they do not exist."""
        self.data_path.mkdir(parents=True, exist_ok=True)
        self.qdrant_path.mkdir(parents=True, exist_ok=True)
        self.openwebui_path.mkdir(parents=True, exist_ok=True)
        self.n8n_path.mkdir(parents=True, exist_ok=True)
        self.kokoro_path.mkdir(parents=True, exist_ok=True)
        self.ingest_path.mkdir(parents=True, exist_ok=True)

# Instantiate settings
settings = AppSettings()
settings.ensure_directories()
