"""
Configuration settings for Mini-CRM application.
Uses Pydantic BaseSettings to load environment variables with robust defaults.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Mini-CRM"
    PROJECT_DESCRIPTION: str = "Lead Management System API & Dashboard"
    PROJECT_VERSION: str = "1.0.0"
    
    # Security & JWT settings
    SECRET_KEY: str = "mini-crm-super-secure-secret-key-change-in-production-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Relational Database connection URL
    # Supports SQLite by default for zero-setup, and PostgreSQL via DATABASE_URL env
    DATABASE_URL: str = "sqlite:///./crm.db"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
