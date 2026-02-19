"""
Salon Flow - API Service
Main FastAPI application for core business logic
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import structlog

from app.core.config import settings
from app.core.firebase import init_firebase
from app.core.redis import redis_client
from app.api import auth, tenants, bookings, customers, services, staff

logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Salon Flow API Service")
    init_firebase()
    await redis_client.connect()
    logger.info("Connected to Redis")
    
    yield
    
    # Shutdown
    await redis_client.disconnect()
    logger.info("Shutting down Salon Flow API Service")

app = FastAPI(
    title="Salon Flow API",
    description="AI-powered Salon Management SaaS Platform",
    version="0.1.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(tenants.router, prefix="/api/v1/tenants", tags=["Tenants"])
app.include_router(bookings.router, prefix="/api/v1/bookings", tags=["Bookings"])
app.include_router(customers.router, prefix="/api/v1/customers", tags=["Customers"])
app.include_router(services.router, prefix="/api/v1/services", tags=["Services"])
app.include_router(staff.router, prefix="/api/v1/staff", tags=["Staff"])

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "api-service"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Salon Flow API",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
