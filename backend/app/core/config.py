"""
Configuration settings for the IBS Wellness Companion application.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # App Info
    APP_NAME: str = "IBS Wellness Companion API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "AI-powered IBS management platform with predictive analytics and personalized recommendations"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS: int = 1
    EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS: int = 24
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/ibs_wellness"
    DATABASE_ECHO: bool = False
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001,http://localhost:8000,http://127.0.0.1:8000,http://localhost:8001,http://127.0.0.1:8001"
    ALLOWED_HOSTS: str = "localhost,127.0.0.1"
    
    @property
    def BACKEND_CORS_ORIGINS(self) -> list[str]:
        """Convert CORS_ORIGINS string to list."""
        return self.CORS_ORIGINS.split(",")
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Email
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    # ML Model
    ML_MODEL_PATH: str = "models/"
    ENABLE_ML_PREDICTIONS: bool = True
    
    # ChromaDB
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8001
    CHROMA_COLLECTION_NAME: str = "ibs_knowledge"
    
    # File Upload
    MAX_FILE_SIZE: int = 10485760
    UPLOAD_DIR: str = "uploads/"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    OPENAI_MAX_TOKENS: int = 1000
    
    # OAuth Configuration
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None

    # Firebase Admin
    FIREBASE_PROJECT_ID: Optional[str] = None
    FIREBASE_PRIVATE_KEY_ID: Optional[str] = None
    FIREBASE_PRIVATE_KEY: Optional[str] = None
    FIREBASE_CLIENT_EMAIL: Optional[str] = None
    FIREBASE_CLIENT_ID: Optional[str] = None
    FIREBASE_AUTH_URI: str = "https://accounts.google.com/o/oauth2/auth"
    FIREBASE_TOKEN_URI: str = "https://oauth2.googleapis.com/token"
    FIREBASE_AUTH_PROVIDER_X509_CERT_URL: str = "https://www.googleapis.com/oauth2/v1/certs"
    FIREBASE_CLIENT_X509_CERT_URL: Optional[str] = None
    FIREBASE_UNIVERSE_DOMAIN: str = "googleapis.com"
    FIREBASE_TYPE: str = "service_account"
    FIREBASE_AUDIENCE: Optional[str] = None
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields to prevent validation errors


# Global settings instance
settings = Settings()