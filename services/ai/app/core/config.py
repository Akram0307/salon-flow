"""AI Service Configuration"""
from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Service info
    app_name: str = "Salon Flow AI Service"
    app_version: str = "0.1.0"
    debug: bool = False
    
    # OpenRouter Configuration
    openrouter_api_key: str
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_site_url: str = "https://salonflow.app"
    openrouter_site_name: str = "Salon Flow"
    
    # Model Configuration
    default_model: str = "google/gemini-2.0-flash-exp:free"
    fallback_model: str = "google/gemini-flash-1.5"
    max_tokens: int = 4096
    temperature: float = 0.7
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379/2"
    cache_ttl: int = 3600  # 1 hour
    
    # API Service URL (for fetching salon data)
    api_service_url: str = "http://localhost:8000"
    
    # Feature flags
    enable_cache: bool = True
    enable_logging: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
