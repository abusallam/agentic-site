"""
Configuration management for the enhanced agentic backend stack
"""
import os
from typing import Optional
from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # FastAPI Configuration
    app_name: str = "Agentic Foundation Platform"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    
    # Celery Configuration
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"
    celery_task_serializer: str = "json"
    celery_result_serializer: str = "json"
    celery_accept_content: list = ["json"]
    celery_timezone: str = "UTC"
    celery_enable_utc: bool = True
    
    # Flower Configuration
    flower_port: int = 5555
    flower_url_prefix: str = "/flower"
    
    # Database Configuration
    database_url: Optional[str] = None
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None
    
    # AI Framework Configuration
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    
    # Security Configuration
    secret_key: str = "your-secret-key-change-in-production"
    access_token_expire_minutes: int = 30
    
    # Monitoring Configuration
    enable_prometheus: bool = True
    prometheus_port: int = 8001
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()