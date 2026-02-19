"""Application configuration"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Application
    ENVIRONMENT: str = "development"
    APP_NAME: str = "Salon Flow API"
    DEBUG: bool = True
    
    # Firebase
    FIREBASE_PROJECT_ID: str = "salon-flow-dev"
    FIRESTORE_EMULATOR_HOST: str = "localhost:8080"
    FIREBASE_AUTH_EMULATOR_HOST: str = "localhost:9099"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # OpenRouter
    OPENROUTER_API_KEY: str = ""
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:3003"]
    
    # JWT
    JWT_SECRET: str = "dev-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION: int = 3600  # 1 hour
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
