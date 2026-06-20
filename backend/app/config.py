"""
AWS Infra Vision - Backend Configuration
Production-ready configuration management
"""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application
    APP_NAME: str = "AWS Infra Vision"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = Field(
        default="sqlite:///./aws_infra_vision.db",
        description="SQLite database URL"
    )
    
    # Server
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    WORKERS: int = 1
    
    # AWS
    AWS_DEFAULT_REGION: str = "us-east-1"
    SCAN_TIMEOUT: int = 300  # seconds
    MAX_CONCURRENT_SCANS: int = 5
    
    # Security
    SECRET_KEY: str = Field(
        default_factory=lambda: os.urandom(32).hex(),
        description="Secret key for encryption"
    )
    CREDENTIAL_ENCRYPTION_KEY: Optional[str] = None
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "aws-infra-vision.log"
    LOG_MAX_BYTES: int = 100 * 1024 * 1024  # 100MB
    LOG_BACKUP_COUNT: int = 5
    
    # Performance
    CACHE_TTL: int = 300  # seconds
    MAX_RESOURCES_PER_PAGE: int = 100
    DEFAULT_PAGE_SIZE: int = 20
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()

# Database path resolution
BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR.parent / "data" / "aws_infra_vision.db"
DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
