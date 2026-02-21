"""Notification Service Configuration"""
import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings with GCP Secret Manager support"""
    
    # Application
    app_name: str = "Salon Flow Notification Service"
    app_version: str = "0.1.0"
    debug: bool = False
    
    # GCP Project
    gcp_project_id: str = "salon-saas-487508"
    
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
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


# Singleton settings instance
settings = Settings()
