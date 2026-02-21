"""
Salon Flow - Notification Service
WhatsApp, SMS, Voice notifications via Twilio
"""
import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog

from app.config import settings
from app.router import router as notification_router

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown"""
    # Startup
    logger.info(
        "Starting Notification Service",
        app_name=settings.app_name,
        version=settings.app_version
    )
    
    # Load secrets from GCP Secret Manager if running on Cloud Run
    if os.getenv("K_SERVICE"):
        logger.info("Running on Cloud Run, loading secrets from Secret Manager")
        await load_secrets_from_gcp()
    
    # Validate Twilio configuration
    if settings.twilio_account_sid and settings.twilio_auth_token:
        logger.info(
            "Twilio credentials loaded",
            account_sid_prefix=settings.twilio_account_sid[:8] + "...",
            whatsapp_number=settings.twilio_whatsapp_number
        )
    else:
        logger.warning("Twilio credentials not configured - messaging will be unavailable")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Notification Service")


async def load_secrets_from_gcp():
    """Load secrets from GCP Secret Manager"""
    try:
        from google.cloud import secretmanager
        
        project_id = settings.gcp_project_id
        client = secretmanager.SecretManagerServiceClient()
        
        # Map of secret names to settings attributes
        secrets_to_load = {
            "twilio-account-sid": "twilio_account_sid",
            "twilio-auth-token": "twilio_auth_token",
            "twilio-api-key-sid": "twilio_api_key_sid",
            "twilio-api-key-secret": "twilio_api_key_secret",
        }
        
        for secret_id, attr_name in secrets_to_load.items():
            try:
                name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
                response = client.access_secret_version(request={"name": name})
                value = response.payload.data.decode("UTF-8")
                setattr(settings, attr_name, value)
                logger.info(f"Loaded secret: {secret_id}")
            except Exception as e:
                logger.warning(f"Could not load secret {secret_id}: {e}")
        
        
        # WhatsApp number from environment (not a secret)
        if os.getenv("TWILIO_WHATSAPP_NUMBER"):
            settings.twilio_whatsapp_number = os.getenv("TWILIO_WHATSAPP_NUMBER")
            
    except Exception as e:
        logger.error(f"Error loading secrets from GCP: {e}")


app = FastAPI(
    title=settings.app_name,
    description="Notification Service for Salon Management - WhatsApp, SMS, Voice",
    version=settings.app_version,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(notification_router, prefix="/api/v1", tags=["notifications"])


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "notification-service",
        "version": settings.app_version,
        "twilio_configured": bool(settings.twilio_account_sid),
        "whatsapp_configured": bool(settings.twilio_whatsapp_number)
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "endpoints": {
            "health": "/health",
            "whatsapp": "/api/v1/whatsapp/send",
            "sms": "/api/v1/sms/send",
            "test": "/api/v1/test",
            "status": "/api/v1/status"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
