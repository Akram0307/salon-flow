"""
Salon Flow - API Service
Main FastAPI application for core business logic
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import structlog
import os
import asyncio

from app.core.config import settings
from app.core.firebase import init_firebase, close_firestore
from app.core.redis import redis_client
from app.core.middleware import (
    GZipMiddleware,
    CacheControlMiddleware,
    PerformanceHeadersMiddleware,
    RequestLoggingMiddleware,
)
from app.api import (
    auth_router,
    tenants_router,
    customers_router,
    staff_router,
    services_router,
    bookings_router,
    payments_router,
    memberships_router,
    resources_router,
    shifts_router,
    integrations_router,
    billing_router,
)
from app.api.ai_proxy import router as ai_router
from app.api.onboarding import router as onboarding_router

logger = structlog.get_logger()

# Track initialization status
firebase_ready = False
redis_ready = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events with optimized resource management."""
    global firebase_ready, redis_ready
    
    # Startup
    logger.info("Starting Salon Flow API Service", environment=settings.ENVIRONMENT)

    # Initialize Firebase (non-blocking with error handling)
    try:
        init_firebase()
        firebase_ready = True
        logger.info("Firebase initialized successfully")
    except Exception as e:
        logger.warning("Firebase initialization failed - some features may be limited", error=str(e))
        firebase_ready = False

    # Connect to Redis (non-blocking with error handling)
    try:
        await asyncio.wait_for(redis_client.connect(), timeout=5.0)
        redis_ready = True
        logger.info("Redis connected with connection pool")
    except asyncio.TimeoutError:
        logger.warning("Redis connection timeout - running without cache")
        redis_ready = False
    except Exception as e:
        logger.warning("Redis connection failed - running without cache", error=str(e))
        redis_ready = False

    yield

    # Shutdown - graceful cleanup
    logger.info("Shutting down Salon Flow API Service")

    # Close Redis connections
    if redis_ready:
        try:
            await redis_client.disconnect()
            logger.info("Redis connections closed")
        except Exception as e:
            logger.warning("Error closing Redis", error=str(e))

    # Close Firestore connections
    if firebase_ready:
        try:
            await close_firestore()
            logger.info("Firestore connections closed")
        except Exception as e:
            logger.warning("Error closing Firestore", error=str(e))


app = FastAPI(
    title="Salon Flow API",
    description="AI-powered Salon Management SaaS Platform",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS Configuration
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
    "http://localhost:5176",
    "https://salon-flow-client.web.app",
    "https://salon-flow-staff.web.app",
    "https://salon-flow-manager.web.app",
    "https://salon-flow-owner.web.app",
    "https://salon-flow-client.firebaseapp.com",
    "https://salon-flow-staff.firebaseapp.com",
    "https://salon-flow-manager.firebaseapp.com",
    "https://salon-flow-owner.firebaseapp.com",
]

# Add production URLs from environment
# Add production URLs from environment
if hasattr(settings, 'CORS_ORIGINS') and settings.CORS_ORIGINS:
    if isinstance(settings.CORS_ORIGINS, list):
        allowed_origins.extend(settings.CORS_ORIGINS)
    elif isinstance(settings.CORS_ORIGINS, str):
        allowed_origins.extend(settings.CORS_ORIGINS.split(','))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(CacheControlMiddleware)
app.add_middleware(PerformanceHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)

# Health check endpoint - must work even if Firebase/Redis are not ready
@app.get("/health")
async def health_check():
    """Health check endpoint for Cloud Run."""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "firebase": "ready" if firebase_ready else "not_ready",
        "redis": "ready" if redis_ready else "not_ready",
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Salon Flow API",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
    }


# Include routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(tenants_router, prefix="/api/v1/tenants", tags=["Tenants"])
app.include_router(customers_router, prefix="/api/v1/customers", tags=["Customers"])
app.include_router(staff_router, prefix="/api/v1/staff", tags=["Staff"])
app.include_router(services_router, prefix="/api/v1/services", tags=["Services"])
app.include_router(bookings_router, prefix="/api/v1/bookings", tags=["Bookings"])
app.include_router(payments_router, prefix="/api/v1/payments", tags=["Payments"])
app.include_router(memberships_router, prefix="/api/v1/memberships", tags=["Memberships"])
app.include_router(resources_router, prefix="/api/v1/resources", tags=["Resources"])
app.include_router(shifts_router, prefix="/api/v1/shifts", tags=["Shifts"])
app.include_router(integrations_router, prefix="/api/v1/integrations", tags=["Integrations"])
app.include_router(billing_router, prefix="/api/v1/billing", tags=["Billing"])
app.include_router(ai_router, prefix="/api/v1/ai", tags=["AI"])
app.include_router(onboarding_router, prefix="/api/v1/onboarding", tags=["Onboarding"])


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
