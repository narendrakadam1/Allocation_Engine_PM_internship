"""
Configuration settings for PM Internship AI Engine

This module contains all configuration settings for the application,
including database, security, AI models, and external service configurations.
"""

from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import List, Optional, Any, Dict
import secrets
import os


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application Settings
    APP_NAME: str = "PM Internship AI Engine"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=True, env="DEBUG")
    
    # Server Settings
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    ALLOWED_HOSTS: List[str] = Field(
        default=["localhost", "127.0.0.1", "0.0.0.0", "*"],
        env="ALLOWED_HOSTS"
    )
    
    # Security Settings
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32), env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    
    # Database Settings
    DATABASE_URL: str = Field(
        default="postgresql://pm_user:pm_password@localhost:5432/pm_internship_db",
        env="DATABASE_URL"
    )
    DATABASE_POOL_SIZE: int = Field(default=10, env="DATABASE_POOL_SIZE")
    DATABASE_MAX_OVERFLOW: int = Field(default=20, env="DATABASE_MAX_OVERFLOW")
    
    # Redis Settings
    REDIS_URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    REDIS_CACHE_TTL: int = Field(default=3600, env="REDIS_CACHE_TTL")  # 1 hour
    
    # Celery Settings
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/0", env="CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/0", env="CELERY_RESULT_BACKEND")
    
    # AI Model Settings
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    OPENAI_MODEL: str = Field(default="gpt-4", env="OPENAI_MODEL")
    EMBEDDING_MODEL: str = Field(default="text-embedding-ada-002", env="EMBEDDING_MODEL")
    
    # Hugging Face Settings
    HUGGINGFACE_API_KEY: Optional[str] = Field(default=None, env="HUGGINGFACE_API_KEY")
    SENTENCE_TRANSFORMER_MODEL: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        env="SENTENCE_TRANSFORMER_MODEL"
    )
    
    # File Upload Settings
    MAX_FILE_SIZE: int = Field(default=10 * 1024 * 1024, env="MAX_FILE_SIZE")  # 10MB
    ALLOWED_FILE_TYPES: List[str] = Field(
        default=["pdf", "doc", "docx", "jpg", "jpeg", "png"],
        env="ALLOWED_FILE_TYPES"
    )
    UPLOAD_DIR: str = Field(default="uploads", env="UPLOAD_DIR")
    
    # Email Settings
    SMTP_HOST: Optional[str] = Field(default=None, env="SMTP_HOST")
    SMTP_PORT: int = Field(default=587, env="SMTP_PORT")
    SMTP_USERNAME: Optional[str] = Field(default=None, env="SMTP_USERNAME")
    SMTP_PASSWORD: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    SMTP_TLS: bool = Field(default=True, env="SMTP_TLS")
    FROM_EMAIL: str = Field(default="noreply@pm-internship-ai.gov.in", env="FROM_EMAIL")
    
    # SMS Settings (Twilio)
    TWILIO_ACCOUNT_SID: Optional[str] = Field(default=None, env="TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN: Optional[str] = Field(default=None, env="TWILIO_AUTH_TOKEN")
    TWILIO_PHONE_NUMBER: Optional[str] = Field(default=None, env="TWILIO_PHONE_NUMBER")
    
    # Push Notification Settings
    FCM_SERVER_KEY: Optional[str] = Field(default=None, env="FCM_SERVER_KEY")
    
    # External API Settings
    AADHAAR_API_URL: Optional[str] = Field(default=None, env="AADHAAR_API_URL")
    AADHAAR_API_KEY: Optional[str] = Field(default=None, env="AADHAAR_API_KEY")
    
    DIGILOCKER_API_URL: Optional[str] = Field(default=None, env="DIGILOCKER_API_URL")
    DIGILOCKER_API_KEY: Optional[str] = Field(default=None, env="DIGILOCKER_API_KEY")
    
    # LinkedIn API
    LINKEDIN_CLIENT_ID: Optional[str] = Field(default=None, env="LINKEDIN_CLIENT_ID")
    LINKEDIN_CLIENT_SECRET: Optional[str] = Field(default=None, env="LINKEDIN_CLIENT_SECRET")
    
    # GitHub API
    GITHUB_CLIENT_ID: Optional[str] = Field(default=None, env="GITHUB_CLIENT_ID")
    GITHUB_CLIENT_SECRET: Optional[str] = Field(default=None, env="GITHUB_CLIENT_SECRET")
    
    # Google APIs
    GOOGLE_CLIENT_ID: Optional[str] = Field(default=None, env="GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: Optional[str] = Field(default=None, env="GOOGLE_CLIENT_SECRET")
    
    # Blockchain Settings
    BLOCKCHAIN_NETWORK: str = Field(default="ethereum", env="BLOCKCHAIN_NETWORK")
    WEB3_PROVIDER_URL: Optional[str] = Field(default=None, env="WEB3_PROVIDER_URL")
    SMART_CONTRACT_ADDRESS: Optional[str] = Field(default=None, env="SMART_CONTRACT_ADDRESS")
    
    # Monitoring Settings
    SENTRY_DSN: Optional[str] = Field(default=None, env="SENTRY_DSN")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    
    # Elasticsearch Settings
    ELASTICSEARCH_URL: str = Field(default="http://localhost:9200", env="ELASTICSEARCH_URL")
    ELASTICSEARCH_INDEX: str = Field(default="pm_internship", env="ELASTICSEARCH_INDEX")
    
    # MinIO/S3 Settings
    MINIO_ENDPOINT: str = Field(default="localhost:9000", env="MINIO_ENDPOINT")
    MINIO_ACCESS_KEY: str = Field(default="minioadmin", env="MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY: str = Field(default="minioadmin123", env="MINIO_SECRET_KEY")
    MINIO_BUCKET: str = Field(default="pm-internship-files", env="MINIO_BUCKET")
    
    # AI Matching Settings
    MATCHING_THRESHOLD: float = Field(default=0.7, env="MATCHING_THRESHOLD")
    MAX_MATCHES_PER_STUDENT: int = Field(default=10, env="MAX_MATCHES_PER_STUDENT")
    BIAS_DETECTION_ENABLED: bool = Field(default=True, env="BIAS_DETECTION_ENABLED")
    
    # Workflow Automation
    N8N_API_URL: Optional[str] = Field(default=None, env="N8N_API_URL")
    N8N_API_KEY: Optional[str] = Field(default=None, env="N8N_API_KEY")
    
    # Language Settings
    DEFAULT_LANGUAGE: str = Field(default="en", env="DEFAULT_LANGUAGE")
    SUPPORTED_LANGUAGES: List[str] = Field(
        default=[
            "en", "hi", "bn", "te", "mr", "ta", "gu", "ur", "kn", "or",
            "ml", "pa", "as", "mai", "mag", "bh", "ne", "sa", "ks", "sd", "kok", "mni"
        ],
        env="SUPPORTED_LANGUAGES"
    )
    
    # Feature Flags
    ENABLE_VIDEO_INTERVIEWS: bool = Field(default=False, env="ENABLE_VIDEO_INTERVIEWS")
    ENABLE_BLOCKCHAIN_AUDIT: bool = Field(default=False, env="ENABLE_BLOCKCHAIN_AUDIT")
    ENABLE_ADVANCED_ANALYTICS: bool = Field(default=True, env="ENABLE_ADVANCED_ANALYTICS")
    ENABLE_MOBILE_APP: bool = Field(default=True, env="ENABLE_MOBILE_APP")
    
    @validator("ALLOWED_HOSTS", pre=True)
    def parse_allowed_hosts(cls, v):
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v
    
    @validator("ALLOWED_FILE_TYPES", pre=True)
    def parse_allowed_file_types(cls, v):
        if isinstance(v, str):
            return [ext.strip() for ext in v.split(",")]
        return v
    
    @validator("SUPPORTED_LANGUAGES", pre=True)
    def parse_supported_languages(cls, v):
        if isinstance(v, str):
            return [lang.strip() for lang in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Create settings instance
settings = Settings()


# Configuration for different environments
class DevelopmentSettings(Settings):
    """Development environment settings"""
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    ENVIRONMENT: str = "development"


class ProductionSettings(Settings):
    """Production environment settings"""
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "production"
    ALLOWED_HOSTS: List[str] = ["pm-internship-ai.gov.in", "api.pm-internship-ai.gov.in"]


class TestingSettings(Settings):
    """Testing environment settings"""
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    ENVIRONMENT: str = "testing"
    DATABASE_URL: str = "sqlite:///./test.db"


def get_settings() -> Settings:
    """Get settings based on environment"""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionSettings()
    elif env == "testing":
        return TestingSettings()
    else:
        return DevelopmentSettings()


# Export the appropriate settings
settings = get_settings()