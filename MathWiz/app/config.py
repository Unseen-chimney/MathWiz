"""
Configuration management for MathWiz.
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    app_name: str = "MathWiz"
    debug: bool = False
    
    # Database
    database_url: str = "sqlite:///./mathwiz.db"
    
    # LLM Configuration
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    default_llm_model: str = "gpt-4"
    
    # RAG Configuration
    vector_db_path: str = "./chroma_db"
    embedding_model: str = "all-MiniLM-L6-v2"
    chunk_size: int = 500
    chunk_overlap: int = 50
    
    # Agent Configuration
    max_retries: int = 3
    confidence_threshold: float = 0.7
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Create settings instance
settings = Settings()
