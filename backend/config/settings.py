"""
Configuration Settings for ResearchNow Backend
Manages environment variables and application settings
"""

import os
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application Settings
    APP_NAME: str = "ResearchNow"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    API_KEY_HEADER: str = "X-API-Key"
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:19006",  # Expo
        "http://localhost:8081",  # React Native Metro
    ]

    # Database Settings
    DATABASE_URL: str = "postgresql://researchnow:password@localhost:5432/researchnow"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # Vector Database (Qdrant)
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION_NAME: str = "papers"
    QDRANT_VECTOR_SIZE: int = 768  # For embedding models

    # Redis Cache
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL: int = 3600  # 1 hour default
    CACHE_ENABLED: bool = True

    # Celery / Task Queue
    CELERY_BROKER_URL: str = "amqp://guest:guest@localhost:5672//"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    # MinIO / S3 Storage
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET_NAME: str = "researchnow-papers"
    MINIO_SECURE: bool = False

    # API Keys for External Services
    # arXiv - No key required
    ARXIV_BASE_URL: str = "http://export.arxiv.org/api/query"
    ARXIV_RATE_LIMIT: int = 3  # Requests per second

    # PubMed Central
    PUBMED_BASE_URL: str = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    PUBMED_API_KEY: str = ""  # Optional, increases rate limits
    PUBMED_EMAIL: str = "your-email@example.com"  # Required by NCBI

    # CORE
    CORE_API_KEY: str = ""  # Register at core.ac.uk
    CORE_BASE_URL: str = "https://api.core.ac.uk/v3"
    CORE_RATE_LIMIT: int = 10

    # Semantic Scholar
    SEMANTIC_SCHOLAR_API_KEY: str = ""  # Optional
    SEMANTIC_SCHOLAR_BASE_URL: str = "https://api.semanticscholar.org/graph/v1"
    SEMANTIC_SCHOLAR_RATE_LIMIT: int = 100

    # Crossref
    CROSSREF_BASE_URL: str = "https://api.crossref.org"
    CROSSREF_EMAIL: str = "your-email@example.com"  # For polite pool
    CROSSREF_RATE_LIMIT: int = 50

    # OpenAlex
    OPENALEX_BASE_URL: str = "https://api.openalex.org"
    OPENALEX_EMAIL: str = "your-email@example.com"  # Recommended
    OPENALEX_RATE_LIMIT: int = 10

    # DOAJ
    DOAJ_API_KEY: str = ""  # Optional
    DOAJ_BASE_URL: str = "https://doaj.org/api/v3"

    # AI Model Settings
    # Llama 70B
    LLAMA_MODEL_NAME: str = "llama2:70b"
    LLAMA_API_URL: str = "http://localhost:11434"  # Ollama default
    LLAMA_TEMPERATURE: float = 0.3
    LLAMA_MAX_TOKENS: int = 2048
    LLAMA_TOP_P: float = 0.9

    # AELLA-Qwen
    AELLA_MODEL_NAME: str = "aella/qwen"
    AELLA_API_URL: str = "http://localhost:8080"
    AELLA_TEMPERATURE: float = 0.3
    AELLA_MAX_TOKENS: int = 2048

    # Embedding Model
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-mpnet-base-v2"
    EMBEDDING_DEVICE: str = "cuda"  # "cuda", "cpu", or "mps"
    EMBEDDING_BATCH_SIZE: int = 32

    # Fallback Models (if local models unavailable)
    OPENAI_API_KEY: str = ""  # Optional
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    ANTHROPIC_API_KEY: str = ""  # Optional
    HUGGINGFACE_TOKEN: str = ""  # For gated models

    # Summarization Settings
    SUMMARY_MIN_LENGTH: int = 100
    SUMMARY_MAX_LENGTH: int = 500
    SUMMARY_EXECUTIVE_LENGTH: int = 200
    SUMMARY_DETAILED_LENGTH: int = 1000
    SUMMARY_SIMPLIFICATION_LEVEL: str = "high"  # "low", "medium", "high"

    # Paper Processing
    MAX_PAPER_SIZE_MB: int = 50
    ALLOWED_PAPER_FORMATS: List[str] = ["pdf", "xml", "txt", "html"]
    PARALLEL_DOWNLOADS: int = 5
    DOWNLOAD_TIMEOUT: int = 300  # 5 minutes

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000

    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # Search Settings
    SEARCH_MIN_SCORE: float = 0.5
    SEARCH_MAX_RESULTS: int = 1000
    SEMANTIC_SEARCH_ENABLED: bool = True

    # Background Jobs
    ENABLE_BACKGROUND_JOBS: bool = True
    PAPER_SYNC_INTERVAL_HOURS: int = 24
    SUMMARY_BATCH_SIZE: int = 10

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # "json" or "text"
    LOG_FILE: str = "logs/researchnow.log"

    # Monitoring
    SENTRY_DSN: str = ""  # Optional
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090

    # Feature Flags
    ENABLE_USER_ACCOUNTS: bool = True
    ENABLE_BOOKMARKS: bool = True
    ENABLE_COLLECTIONS: bool = True
    ENABLE_SHARING: bool = True
    ENABLE_ANNOTATIONS: bool = False  # Future feature
    ENABLE_CITATION_GRAPH: bool = False  # Future feature

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="allow"
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance
    Uses lru_cache to ensure settings are only loaded once
    """
    return Settings()


# Export settings instance
settings = get_settings()
