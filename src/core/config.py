"""
Application configuration using Pydantic Settings.

Load configuration from .env file and environment variables.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""

    # Database
    database_url: str = "sqlite:///./univ_insight.db"
    db_echo: bool = False

    # FastAPI
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = True

    # LLM
    ollama_api_url: str = "http://localhost:11434"
    ollama_model: str = "llama2:latest"

    # Crawler
    crawler_timeout: int = 30
    crawler_retries: int = 3

    # Notion API
    notion_api_key: Optional[str] = None
    notion_database_id: Optional[str] = None

    # Kakao API
    kakao_api_key: Optional[str] = None

    # ChromaDB
    chromadb_path: str = "./chroma_db"
    chromadb_persist: bool = True

    # Application
    log_level: str = "INFO"
    environment: str = "development"

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
