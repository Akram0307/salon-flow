"""
Salon Flow - API Service
Main FastAPI application for core business logic
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import structlog

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
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events with optimized resource management."""
    # Startup
    logger.info("Starting Salon Flow API Service", environment=settings.ENVIRONMENT)

    # Initialize Firebase (singleton async client)
    init_firebase()
    logger.info("Firebase initialized")

    # Connect to Redis with connection pooling
    try:
        await redis_client.connect()
        logger.info("Redis connected with connection pool", 
                   max_connections=redis_client.pool_settings["max_connections"])
    except Exception as e:
        logger.warning("Redis connection failed - running without cache", error=str(e))

    yield

    # Shutdown - graceful cleanup
    logger.info("Shutting down Salon Flow API Service")

    # Close Redis connections
    try:
        await redis_client.disconnect()
        logger.info("Redis connections closed")
    except Exception as e:
        logger.warning("Error closing Redis", error=str(e))

    # Close Firestore connections
    try:
        await close_firestore()
        logger.info("Firestore connections closed")
    except Exception as e:
        logger.warning("Error closing Firestore", error=str(e))


app = FastAPI(
    title="Salon Flow API",
    description="AI-powered Salon Management SaaS Platform",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# ============================================================================
# Middleware Stack (order matters - last added is first executed)
# ============================================================================

# Request logging and performance tracking
app.add_middleware(RequestLoggingMiddleware)

# Performance headers (X-Process-Time, X-Request-Id)
app.add_middleware(PerformanceHeadersMiddleware)

# Cache control headers for GET requests
app.add_middleware(
    CacheControlMiddleware,
    default_max_age=60,  # 1 minute default
    cache_paths={
        "/api/v1/services": 300,  # 5 minutes for service catalog
        "/api/v1/tenants": 600,  # 10 minutes for tenant config
        "/health": 30,  # 30 seconds for health check
    }
)

# GZip compression for responses > 500 bytes
app.add_middleware(
    GZipMiddleware,
    minimum_size=500,
    compress_level=6,
    exclude_paths=["/docs", "/redoc", "/openapi.json"],
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Routes
# ============================================================================

# Include routers with versioned API prefix
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


@app.get("/health")
async def health_check():
    """Health check endpoint with service status."""
    redis_status = "connected" if redis_client.is_connected else "disconnected"

    return {
        "status": "healthy",
        "service": "api-service",
        "version": "0.1.0",
        "environment": settings.ENVIRONMENT,
        "services": {
            "redis": redis_status,
            "firebase": "initialized"
        }
    }


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to Salon Flow API",
        "version": "0.1.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "endpoints": {
            "auth": "/api/v1/auth",
            "tenants": "/api/v1/tenants",
            "customers": "/api/v1/customers",
            "staff": "/api/v1/staff",
            "services": "/api/v1/services",
            "bookings": "/api/v1/bookings",
            "payments": "/api/v1/payments",
            "memberships": "/api/v1/memberships",
            "resources": "/api/v1/resources",
            "shifts": "/api/v1/shifts"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_config=None,  # Use structlog
    )
