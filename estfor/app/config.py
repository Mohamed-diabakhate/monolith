"""
Configuration settings for the EstFor Asset Collection System.
"""

from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # API Configuration
    API_HOST: str = Field(default="0.0.0.0", env="API_HOST")
    API_PORT: int = Field(default=8000, env="API_PORT")
    ALLOWED_ORIGINS: List[str] = Field(default=["*"], env="ALLOWED_ORIGINS")
    
    # EstFor API Configuration
    ESTFOR_API_URL: str = Field(default="https://api.estfor.com", env="ESTFOR_API_URL")
    # EstFor API doesn't require authentication
    # ESTFOR_API_KEY: str = Field(env="ESTFOR_API_KEY")
    ESTFOR_RATE_LIMIT: int = Field(default=100, env="ESTFOR_RATE_LIMIT")
    
    # MongoDB Configuration
    MONGODB_URI: str = Field(default="mongodb://localhost:27017/", env="MONGODB_URI")
    MONGODB_DATABASE: str = Field(default="estfor", env="MONGODB_DATABASE")
    MONGODB_COLLECTION: str = Field(default="all_assets", env="MONGODB_COLLECTION")
    MONGODB_MAX_POOL_SIZE: int = Field(default=10, env="MONGODB_MAX_POOL_SIZE")
    
    # Redis Configuration
    REDIS_URL: str = Field(default="redis://redis:6379/0", env="REDIS_URL")
    REDIS_PASSWORD: str = Field(default="", env="REDIS_PASSWORD")
    
    # Celery Configuration
    CELERY_BROKER_URL: str = Field(default="redis://redis:6379/1", env="CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = Field(default="redis://redis:6379/2", env="CELERY_RESULT_BACKEND")
    
    # Security
    SECRET_KEY: str = Field(env="SECRET_KEY", default="your-secret-key-change-in-production")
    API_KEY_HEADER: str = Field(default="X-API-Key", env="API_KEY_HEADER")
    
    # Monitoring
    PROMETHEUS_MULTIPROC_DIR: str = Field(default="/tmp", env="PROMETHEUS_MULTIPROC_DIR")
    
    # Performance
    MAX_WORKERS: int = Field(default=4, env="MAX_WORKERS")
    WORKER_TIMEOUT: int = Field(default=300, env="WORKER_TIMEOUT")
    
    # Container Management Configuration
    CONTAINER_AUTO_START: bool = Field(default=True, env="CONTAINER_AUTO_START")
    CONTAINER_AUTO_STOP: bool = Field(default=True, env="CONTAINER_AUTO_STOP")
    CONTAINER_IDLE_TIMEOUT: int = Field(default=30, env="CONTAINER_IDLE_TIMEOUT")  # minutes
    CONTAINER_HIGH_IDLE_TIMEOUT: int = Field(default=120, env="CONTAINER_HIGH_IDLE_TIMEOUT")  # minutes
    CONTAINER_LOW_IDLE_TIMEOUT: int = Field(default=10, env="CONTAINER_LOW_IDLE_TIMEOUT")  # minutes
    CONTAINER_STARTUP_TIMEOUT: int = Field(default=60, env="CONTAINER_STARTUP_TIMEOUT")  # seconds
    CONTAINER_HEALTH_CHECK_INTERVAL: int = Field(default=30, env="CONTAINER_HEALTH_CHECK_INTERVAL")  # seconds
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings() 