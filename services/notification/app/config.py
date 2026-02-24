"""Notification Service Configuration"""
import os
from pydantic_settings import BaseSettings
from typing import Optional, List


class Settings(BaseSettings):
    """Application settings with GCP Secret Manager support"""
    
    # Application
    app_name: str = "Salon Flow Notification Service"
    app_version: str = "0.1.0"
    debug: bool = False
    environment: str = "development"
    
    # GCP Project
    gcp_project_id: str = "salon-saas-487508"
    
    # Firebase (for JWT verification)
    firebase_project_id: str = "salon-saas-487508"
    
    # JWT Authentication - must match API service
    jwt_secret: str = ""  # Must be set via env, same as API service
    jwt_algorithm: str = "HS256"
    
    # Twilio - Platform Level (from GCP Secret Manager or env)
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_api_key_sid: Optional[str] = None
    twilio_api_key_secret: Optional[str] = None
    twilio_whatsapp_number: Optional[str] = None  # Platform default WhatsApp number
    
    # Redis
    upstash_redis_rest_url: Optional[str] = None
    upstash_redis_rest_token: Optional[str] = None
    
    # Feature Flags
    use_platform_twilio: bool = True  # Default to platform credentials
    
    # CORS - Same as API service
    cors_origins: List[str] = [
        # Local development
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:3003",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:5176",
        # Production Cloud Run URLs
        "https://salon-flow-owner-rgvcleapsa-el.a.run.app",
        "https://salon-flow-manager-rgvcleapsa-el.a.run.app",
        "https://salon-flow-staff-rgvcleapsa-el.a.run.app",
        "https://salon-flow-client-rgvcleapsa-el.a.run.app",
        # API and AI services (for internal calls)
        "https://salon-flow-api-rgvcleapsa-el.a.run.app",
        "https://salon-flow-ai-rgvcleapsa-el.a.run.app",
    ]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


# Singleton settings instance
settings = Settings()
