"""
Configuration management for the RAG API application.
"""
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from functools import lru_cache
from pathlib import Path

# Project root: 3 levels up from this file (backend/app/core/config.py -> project_root/)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Ollama Configuration
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"
    
    # ChromaDB Configuration
    chroma_persist_directory: str = str(PROJECT_ROOT / "data" / "chroma_db")
    chroma_collection_name: str = "basecamp_handbook"
    
    # Embedding Model
    embedding_model: str = "all-MiniLM-L6-v2"
    
    # Application Settings
    app_title: str = "Basecamp Handbook RAG API"
    app_version: str = "2.0.0"
    docs_directory: str = str(PROJECT_ROOT / "knowledge_base")
    
    # RAG Settings
    chunk_size: int = 800
    chunk_overlap: int = 200
    top_k_results: int = 5
    temperature: float = 0.3
    
    # Prompts Configuration
    prompts_config_path: str = str(PROJECT_ROOT / "backend" / "app" / "llm" / "prompt_templates.yaml")
    
    # API Settings
    api_v1_prefix: str = "/api/v1"
    
    # Logging
    log_level: str = "INFO"
    log_dir: str = str(PROJECT_ROOT / "data" / "logs")
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Returns:
        Settings: Application settings singleton
    """
    return Settings()
