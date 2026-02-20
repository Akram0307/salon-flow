"""
Salon Flow - AI Agent Service
AI-powered features: Chat, Marketing, Analytics

Uses OpenRouter for Gemini model access with Redis caching.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog

from app.core.config import get_settings
from app.core.logging import configure_logging
from app.api import chat, marketing, analytics
from app.services.openrouter_client import get_openrouter_client
from app.services.cache_service import get_cache_service

settings = get_settings()
configure_logging()
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("ai_service_starting", version=settings.app_version)
    
    # Initialize connections
    try:
        client = await get_openrouter_client()
        logger.info("openrouter_connected", model=settings.default_model)
    except Exception as e:
        logger.warning("openrouter_connection_failed", error=str(e))
    
    try:
        cache = await get_cache_service()
        logger.info("redis_connected", url=settings.redis_url)
    except Exception as e:
        logger.warning("redis_connection_failed", error=str(e))
    
    yield
    
    # Shutdown
    logger.info("ai_service_shutting_down")
    if client:
        await client.close()
    if cache:
        await cache.close()


app = FastAPI(
    title="Salon Flow AI Service",
    description="AI Agent Service for Salon Management - Powered by OpenRouter & Gemini",
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api/v1")
app.include_router(marketing.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    openrouter_status = "connected"
    redis_status = "connected"
    
    # Check OpenRouter
    try:
        client = await get_openrouter_client()
        # Simple test - just check client exists
        if not client.api_key:
            openrouter_status = "not_configured"
    except Exception as e:
        openrouter_status = f"error: {str(e)[:50]}"
    
    # Check Redis
    try:
        cache = await get_cache_service()
        if cache._client:
            await cache._client.ping()
    except Exception as e:
        redis_status = f"error: {str(e)[:50]}"
    
    return {
        "status": "healthy" if openrouter_status == "connected" else "degraded",
        "service": "ai-service",
        "version": settings.app_version,
        "openrouter": openrouter_status,
        "redis": redis_status,
        "default_model": settings.default_model,
    }


@app.get("/models")
async def list_models():
    """List available AI models"""
    return {
        "default": settings.default_model,
        "fallback": settings.fallback_model,
        "available": [
            {"id": "google/gemini-2.0-flash-exp:free", "name": "Gemini 2.0 Flash (Free)", "type": "chat"},
            {"id": "google/gemini-flash-1.5", "name": "Gemini 1.5 Flash", "type": "chat"},
            {"id": "google/gemini-pro-1.5", "name": "Gemini 1.5 Pro", "type": "chat"},
        ]
    }


@app.get("/agents")
async def list_agents():
    """List available AI agents"""
    from app.services.agents import AGENTS
    
    return {
        "agents": [
            {
                "type": agent_type,
                "name": agent_class.name,
                "description": agent_class.description,
            }
            for agent_type, agent_class in AGENTS.items()
        ]
    }


@app.post("/generate")
async def generate_text(
    prompt: str,
    system_prompt: str = None,
    model: str = None,
):
    """Direct text generation endpoint"""
    client = await get_openrouter_client()
    
    response = await client.chat(
        prompt=prompt,
        system_prompt=system_prompt,
        model=model,
    )
    
    return {
        "response": response.content,
        "model": response.model,
        "usage": response.usage,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.debug,
    )
