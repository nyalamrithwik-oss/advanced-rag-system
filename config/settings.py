"""
Configuration Settings Module

Handles environment variables and application settings.

Author: RAG Learning Journey - Day 16
"""

import os
from typing import Optional
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # API Keys
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    pinecone_api_key: str = Field(default="", env="PINECONE_API_KEY")
    cohere_api_key: str = Field(default="", env="COHERE_API_KEY")

    # Pinecone Configuration
    pinecone_index_name: str = Field(default="advanced-rag", env="PINECONE_INDEX_NAME")
    pinecone_environment: str = Field(
        default="us-east-1", env="PINECONE_ENVIRONMENT"
    )

    # LLM Configuration
    llm_model: str = Field(default="gpt-4-turbo-preview", env="LLM_MODEL")
    embedding_model: str = Field(
        default="text-embedding-3-small", env="EMBEDDING_MODEL"
    )
    reranker_model: str = Field(default="rerank-english-v3.0", env="RERANKER_MODEL")

    # RAG Configuration
    chunk_size: int = Field(default=500, env="CHUNK_SIZE")
    chunk_overlap: int = Field(default=100, env="CHUNK_OVERLAP")
    max_retrieved_docs: int = Field(default=10, env="MAX_RETRIEVED_DOCS")
    similarity_threshold: float = Field(default=0.95, env="SIMILARITY_THRESHOLD")

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: Optional[str] = Field(default=None, env="LOG_FILE")

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def validate_settings() -> bool:
    """Validate that all required settings are configured."""
    settings = get_settings()

    required_keys = [
        "openai_api_key",
        "pinecone_api_key",
        "cohere_api_key",
    ]

    missing = []
    for key in required_keys:
        if not getattr(settings, key, ""):
            missing.append(key)

    if missing:
        print(f"⚠️  Missing required environment variables: {', '.join(missing)}")
        return False

    print("✅ All required settings configured")
    return True


if __name__ == "__main__":
    settings = get_settings()
    print("\n=== Current Settings ===")
    for key, value in settings.dict().items():
        if "key" in key.lower():
            display_value = f"{value[:10]}***" if value else "(not set)"
        else:
            display_value = value
        print(f"{key}: {display_value}")

    print("\n=== Validation ===")
    validate_settings()
