"""Pipeline Layer for Request Processing

Implements the Pipeline pattern with middleware chain for:
- Guardrails (salon-only validation)
- Caching (exact + semantic via GCP Vertex AI Vector Search)
- Model Routing (tier-based selection)
- Logging and Metrics
- Rate Limiting

Usage:
    from app.pipeline import RequestProcessor, get_processor
    
    # Get the processor
    processor = get_processor()
    await processor.initialize()
    
    # Process a request
    result = await processor.execute_agent(
        "booking",
        {"prompt": "Book a haircut"},
        {"salon_id": "salon_123"}
    )
"""
from .middleware import (
    BaseMiddleware,
    MiddlewareContext,
    MiddlewareResult,
    GuardrailMiddleware,
    CacheMiddleware,
    ModelRouterMiddleware,
    LoggingMiddleware,
    RateLimitMiddleware,
)
from .processor import (
    RequestProcessor,
    PipelineConfig,
    get_processor,
    initialize_pipeline,
)

__all__ = [
    # Middleware
    "BaseMiddleware",
    "MiddlewareContext",
    "MiddlewareResult",
    "GuardrailMiddleware",
    "CacheMiddleware",
    "ModelRouterMiddleware",
    "LoggingMiddleware",
    "RateLimitMiddleware",
    # Processor
    "RequestProcessor",
    "PipelineConfig",
    "get_processor",
    "initialize_pipeline",
]
