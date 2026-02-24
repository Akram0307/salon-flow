"""Application configuration with Cloud Run support."""
import os
import secrets
from typing import List, Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    ENVIRONMENT: str = "development"
    APP_NAME: str = "Salon Flow API"
    DEBUG: bool = True
    PORT: int = 8080  # Cloud Run default port
    
    # Security - MUST be set via environment variable in production
    # SECRET_KEY is used for session signing and general security
    SECRET_KEY: str = ""  # No default - must be set via env
    
    # JWT Authentication
    JWT_SECRET: str = ""  # No default - must be set via env
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION: int = 3600  # 1 hour
    JWT_REFRESH_EXPIRATION: int = 604800  # 7 days
    
    # Firebase
    FIREBASE_PROJECT_ID: str = "salon-saas-487508"
    FIRESTORE_EMULATOR_HOST: str = ""
    FIREBASE_AUTH_EMULATOR_HOST: str = ""
    
    # GCP
    GCP_PROJECT_ID: str = "salon-saas-487508"
    PUBSUB_TOPIC: str = "salon-events"
    
    # AI Service
    AI_SERVICE_URL: str = "http://localhost:8081"  # Default for local dev
    AI_SERVICE_TIMEOUT: int = 60  # seconds
    
    # Redis - Support both local and Upstash (serverless)
    # Upstash uses rediss:// (TLS) format
    REDIS_URL: str = "redis://localhost:6379"
    UPSTASH_REDIS_URL: Optional[str] = None  # Takes precedence if set
    
    # OpenRouter
    OPENROUTER_API_KEY: str = ""
    
    # Twilio
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""
    
    # CORS - Production URLs from Cloud Run
    CORS_ORIGINS: List[str] = [
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
    
    # Salon Business Settings
    GST_RATE: float = 5.0  # 5% GST for salon services
    LOYALTY_POINTS_PER_RUPEE: int = 1  # 1 point per ₹10 spent
    LOYALTY_POINT_VALUE: float = 1.0  # ₹1 per point redemption
    LOYALTY_POINTS_EXPIRY_MONTHS: int = 12
    MEMBERSHIP_RENEWAL_DAYS: int = 15  # Days before expiry to prompt renewal
    
    # Booking Settings
    DEFAULT_SLOT_DURATION: int = 30  # minutes
    MAX_FUTURE_BOOKING_DAYS: int = 30
    CANCELLATION_HOURS: int = 2  # Free cancellation up to 2 hours before
    LATE_ARRIVAL_MINUTES: int = 15  # Auto-reschedule after 15 min late
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Generate secrets for development if not set
        if not self.SECRET_KEY:
            if self.ENVIRONMENT == "production":
                raise ValueError("SECRET_KEY must be set in production environment")
            self.SECRET_KEY = secrets.token_urlsafe(32)
        if not self.JWT_SECRET:
            if self.ENVIRONMENT == "production":
                raise ValueError("JWT_SECRET must be set in production environment")
            self.JWT_SECRET = "dev-jwt-secret-key-not-for-production"
    
    @property
    def effective_redis_url(self) -> str:
        """Get the effective Redis URL (Upstash takes precedence)."""
        return self.UPSTASH_REDIS_URL or self.REDIS_URL
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT == "production"
    
    @property
    def is_cloud_run(self) -> bool:
        """Check if running on Cloud Run."""
        return os.getenv("K_SERVICE") is not None
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra env vars


settings = Settings()
