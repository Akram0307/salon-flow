"""Pipeline Middleware for Request Processing

Implements the Pipeline Layer with:
- GuardrailMiddleware: Salon-only validation
- CacheMiddleware: Exact + semantic caching (GCP Vertex AI Vector Search)
- ModelRouterMiddleware: Tier-based model selection
- LoggingMiddleware: Request/response logging
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
import time
import hashlib
import json
import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger()


# ============================================================================
# Base Middleware
# ============================================================================

class MiddlewareContext(BaseModel):
    """Context passed through middleware pipeline"""
    request_id: str = Field(default_factory=lambda: hashlib.md5(str(datetime.utcnow()).encode()).hexdigest()[:12])
    salon_id: Optional[str] = None
    agent_name: Optional[str] = None
    channel: str = "web"
    language: str = "en"
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Pipeline state
    start_time: float = Field(default_factory=time.time)
    cache_hit: bool = False
    guardrail_passed: bool = True
    model_selected: Optional[str] = None
    
    model_config = {"arbitrary_types_allowed": True}


class MiddlewareResult(BaseModel):
    """Result from middleware processing"""
    success: bool = True
    blocked: bool = False
    message: str = ""
    data: Optional[Dict[str, Any]] = None
    cached: bool = False
    skip_remaining: bool = False  # Skip remaining middleware (e.g., cache hit)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BaseMiddleware(ABC):
    """Base class for all middleware"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Middleware name"""
        pass
    
    @abstractmethod
    async def process(
        self,
        request: Dict[str, Any],
        context: MiddlewareContext,
        next_middleware: Callable
    ) -> MiddlewareResult:
        """Process request through middleware"""
        pass
    
    async def initialize(self) -> bool:
        """Initialize middleware resources"""
        return True
    
    async def cleanup(self) -> None:
        """Cleanup middleware resources"""
        pass


# ============================================================================
# Guardrail Middleware
# ============================================================================

class GuardrailMiddleware(BaseMiddleware):
    """Middleware for salon-only query validation.
    
    Ensures all queries are salon-related before processing.
    Supports multiple languages (English, Hindi, Telugu).
    """
    
    def __init__(self):
        self._guardrails = {}
        self._initialized = False
    
    @property
    def name(self) -> str:
        return "guardrail"
    
    async def initialize(self) -> bool:
        """Initialize guardrails for all supported languages"""
        try:
            from app.services.guardrails import SalonGuardrail
            
            # Initialize guardrails for supported languages
            for lang in ["en", "hi", "te"]:
                self._guardrails[lang] = SalonGuardrail()
            
            self._initialized = True
            logger.info("guardrail_middleware_initialized", languages=list(self._guardrails.keys()))
            return True
        except Exception as e:
            logger.error("guardrail_init_failed", error=str(e))
            return False
    
    async def process(
        self,
        request: Dict[str, Any],
        context: MiddlewareContext,
        next_middleware: Callable
    ) -> MiddlewareResult:
        """Validate request against salon guardrails"""
        if not self._initialized:
            await self.initialize()
        
        prompt = request.get("prompt", "")
        language = context.language or "en"
        skip_guardrail = request.get("skip_guardrail", False)
        
        if skip_guardrail:
            context.guardrail_passed = True
            return await next_middleware(request, context)
        
        # Get appropriate guardrail
        guardrail = self._guardrails.get(language, self._guardrails.get("en"))
        
        if guardrail:
            is_valid, reason = guardrail.validate_query(prompt)
            
            if not is_valid:
                logger.info(
                    "guardrail_blocked",
                    request_id=context.request_id,
                    reason=reason,
                    language=language
                )
                context.guardrail_passed = False
                return MiddlewareResult(
                    success=False,
                    blocked=True,
                    message=reason or "This query is not related to salon services.",
                    data={"blocked_reason": reason}
                )
        
        context.guardrail_passed = True
        return await next_middleware(request, context)


# ============================================================================
# Cache Middleware (GCP Vertex AI Vector Search)
# ============================================================================

class CacheMiddleware(BaseMiddleware):
    """Middleware for exact and semantic caching.
    
    Uses:
    - Redis for exact match caching
    - GCP Vertex AI Vector Search for semantic similarity caching
    """
    
    def __init__(
        self,
        redis_client: Optional[Any] = None,
        vector_search_client: Optional[Any] = None,
        exact_ttl: int = 3600,  # 1 hour
        semantic_ttl: int = 7200,  # 2 hours
        similarity_threshold: float = 0.95
    ):
        self._redis = redis_client
        self._vector_search = vector_search_client
        self._exact_ttl = exact_ttl
        self._semantic_ttl = semantic_ttl
        self._similarity_threshold = similarity_threshold
        self._initialized = False
    
    @property
    def name(self) -> str:
        return "cache"
    
    async def initialize(self) -> bool:
        """Initialize cache connections"""
        try:
            # Initialize Redis client if not provided
            if not self._redis:
                import redis.asyncio as redis
                redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")
                self._redis = redis.from_url(redis_url)
            
            # Initialize GCP Vertex AI Vector Search if not provided
            if not self._vector_search:
                self._vector_search = await self._init_vertex_vector_search()
            
            self._initialized = True
            logger.info("cache_middleware_initialized")
            return True
        except Exception as e:
            logger.warning("cache_init_partial", error=str(e))
            # Continue without caching if init fails
            return True
    
    async def _init_vertex_vector_search(self):
        """Initialize GCP Vertex AI Vector Search client"""
        try:
            from google.cloud import aiplatform
            import os
            
            project_id = os.environ.get("GCP_PROJECT_ID", "salon-saas-487508")
            location = os.environ.get("GCP_REGION", "asia-south1")
            index_endpoint = os.environ.get("VERTEX_INDEX_ENDPOINT")
            
            if index_endpoint:
                aiplatform.init(project=project_id, location=location)
                return aiplatform.MatchServiceClient()
            return None
        except Exception as e:
            logger.warning("vertex_vector_search_init_failed", error=str(e))
            return None
    
    def _generate_cache_key(self, prompt: str, salon_id: str, agent_name: str) -> str:
        """Generate cache key for exact matching"""
        content = f"{agent_name}:{salon_id}:{prompt}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    async def _get_exact_cache(self, key: str) -> Optional[Dict[str, Any]]:
        """Get from exact cache (Redis)"""
        if not self._redis:
            return None
        
        try:
            cached = await self._redis.get(f"cache:exact:{key}")
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.warning("exact_cache_get_failed", error=str(e))
        return None
    
    async def _set_exact_cache(self, key: str, value: Dict[str, Any]) -> None:
        """Set in exact cache (Redis)"""
        if not self._redis:
            return
        
        try:
            await self._redis.setex(
                f"cache:exact:{key}",
                self._exact_ttl,
                json.dumps(value)
            )
        except Exception as e:
            logger.warning("exact_cache_set_failed", error=str(e))
    
    async def _get_semantic_cache(self, prompt: str, salon_id: str) -> Optional[Dict[str, Any]]:
        """Get from semantic cache (GCP Vertex AI Vector Search)"""
        if not self._vector_search:
            return None
        
        try:
            # Generate embedding for the query
            embedding = await self._generate_embedding(prompt)
            if not embedding:
                return None
            
            # Search for similar cached queries
            # This would use Vertex AI Vector Search's FindNeighbors API
            # For now, return None as placeholder
            # TODO: Implement actual vector search
            
        except Exception as e:
            logger.warning("semantic_cache_get_failed", error=str(e))
        return None
    
    async def _generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding using Vertex AI"""
        try:
            from vertexai.language_models import TextEmbeddingModel
            
            model = TextEmbeddingModel.from_pretrained("text-embedding-004")
            embeddings = model.get_embeddings([text])
            return embeddings[0].values
        except Exception as e:
            logger.warning("embedding_generation_failed", error=str(e))
            return None
    
    async def process(
        self,
        request: Dict[str, Any],
        context: MiddlewareContext,
        next_middleware: Callable
    ) -> MiddlewareResult:
        """Process request through cache layers"""
        if not self._initialized:
            await self.initialize()
        
        use_cache = request.get("use_cache", True)
        if not use_cache:
            return await next_middleware(request, context)
        
        prompt = request.get("prompt", "")
        salon_id = context.salon_id or "default"
        agent_name = context.agent_name or "default"
        
        # Try exact cache first
        cache_key = self._generate_cache_key(prompt, salon_id, agent_name)
        cached_result = await self._get_exact_cache(cache_key)
        
        if cached_result:
            logger.info(
                "exact_cache_hit",
                request_id=context.request_id,
                agent=agent_name
            )
            context.cache_hit = True
            return MiddlewareResult(
                success=True,
                cached=True,
                data=cached_result,
                skip_remaining=True
            )
        
        # Try semantic cache
        semantic_result = await self._get_semantic_cache(prompt, salon_id)
        if semantic_result:
            logger.info(
                "semantic_cache_hit",
                request_id=context.request_id,
                agent=agent_name
            )
            context.cache_hit = True
            return MiddlewareResult(
                success=True,
                cached=True,
                data=semantic_result,
                skip_remaining=True
            )
        
        # No cache hit, proceed to next middleware
        result = await next_middleware(request, context)
        
        # Cache the result if successful
        if result.success and result.data:
            await self._set_exact_cache(cache_key, result.data)
        
        return result


# ============================================================================
# Model Router Middleware
# ============================================================================

class ModelRouterMiddleware(BaseMiddleware):
    """Middleware for tier-based model selection.
    
    Routes requests to appropriate models based on:
    - Agent tier requirement (economy, standard, premium)
    - Request complexity
    - Current load/cost optimization
    """
    
    MODEL_TIERS = {
        "economy": [
            "google/gemini-2.0-flash-exp:free",
            "google/gemini-flash-1.5"
        ],
        "standard": [
            "google/gemini-2.0-flash-exp",
            "google/gemini-2.0-flash-001"
        ],
        "premium": [
            "google/gemini-2.0-pro-exp-02-05:free",
            "google/gemini-2.0-pro-exp"
        ],
        "image": [
            "google/gemini-3-pro-image-preview"
        ]
    }
    
    def __init__(self, default_tier: str = "standard"):
        self._default_tier = default_tier
        self._model_usage: Dict[str, int] = {}
    
    @property
    def name(self) -> str:
        return "model_router"
    
    def select_model(self, tier: str, capabilities: List[str] = None) -> str:
        """Select appropriate model for tier"""
        # Check for image generation capability
        if capabilities and "image_generation" in capabilities:
            models = self.MODEL_TIERS.get("image", self.MODEL_TIERS["standard"])
        else:
            models = self.MODEL_TIERS.get(tier, self.MODEL_TIERS[self._default_tier])
        
        # Simple round-robin for load balancing
        model = models[0]  # Use first model for now
        self._model_usage[model] = self._model_usage.get(model, 0) + 1
        return model
    
    async def process(
        self,
        request: Dict[str, Any],
        context: MiddlewareContext,
        next_middleware: Callable
    ) -> MiddlewareResult:
        """Route to appropriate model"""
        # Get agent tier from registry or use default
        tier = request.get("model_tier", self._default_tier)
        capabilities = request.get("capabilities", [])
        
        # Allow override in request
        if "model" in request:
            context.model_selected = request["model"]
        else:
            context.model_selected = self.select_model(tier, capabilities)
        
        logger.debug(
            "model_selected",
            request_id=context.request_id,
            model=context.model_selected,
            tier=tier
        )
        
        # Add model to request for downstream use
        request["model"] = context.model_selected
        
        return await next_middleware(request, context)


# ============================================================================
# Logging Middleware
# ============================================================================

class LoggingMiddleware(BaseMiddleware):
    """Middleware for request/response logging and metrics.
    
    Logs:
    - Request details
    - Response status
    - Timing information
    - Error details
    """
    
    def __init__(self, log_level: str = "INFO"):
        self._log_level = log_level
    
    @property
    def name(self) -> str:
        return "logging"
    
    async def process(
        self,
        request: Dict[str, Any],
        context: MiddlewareContext,
        next_middleware: Callable
    ) -> MiddlewareResult:
        """Log request and response"""
        start_time = time.time()
        
        # Log incoming request
        logger.info(
            "request_started",
            request_id=context.request_id,
            agent=context.agent_name,
            salon_id=context.salon_id,
            channel=context.channel,
            prompt_preview=request.get("prompt", "")[:100]
        )
        
        try:
            result = await next_middleware(request, context)
            
            duration_ms = (time.time() - start_time) * 1000
            
            # Log successful response
            logger.info(
                "request_completed",
                request_id=context.request_id,
                agent=context.agent_name,
                duration_ms=round(duration_ms, 2),
                cache_hit=context.cache_hit,
                model=context.model_selected,
                success=result.success,
                blocked=result.blocked
            )
            
            # Add timing to result
            result.metadata["duration_ms"] = round(duration_ms, 2)
            
            return result
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            
            logger.error(
                "request_failed",
                request_id=context.request_id,
                agent=context.agent_name,
                duration_ms=round(duration_ms, 2),
                error=str(e)
            )
            
            return MiddlewareResult(
                success=False,
                message=f"Request failed: {str(e)}",
                metadata={"duration_ms": round(duration_ms, 2)}
            )


# ============================================================================
# Rate Limiting Middleware
# ============================================================================

class RateLimitMiddleware(BaseMiddleware):
    """Middleware for rate limiting requests.
    
    Implements token bucket algorithm per salon.
    """
    
    def __init__(
        self,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000
    ):
        self._rpm = requests_per_minute
        self._rph = requests_per_hour
        self._buckets: Dict[str, Dict[str, Any]] = {}
    
    @property
    def name(self) -> str:
        return "rate_limit"
    
    def _check_rate_limit(self, salon_id: str) -> tuple[bool, str]:
        """Check if request is within rate limits"""
        now = time.time()
        
        if salon_id not in self._buckets:
            self._buckets[salon_id] = {
                "minute_tokens": self._rpm,
                "hour_tokens": self._rph,
                "last_minute_reset": now,
                "last_hour_reset": now
            }
        
        bucket = self._buckets[salon_id]
        
        # Reset tokens if time window passed
        if now - bucket["last_minute_reset"] >= 60:
            bucket["minute_tokens"] = self._rpm
            bucket["last_minute_reset"] = now
        
        if now - bucket["last_hour_reset"] >= 3600:
            bucket["hour_tokens"] = self._rph
            bucket["last_hour_reset"] = now
        
        # Check limits
        if bucket["minute_tokens"] <= 0:
            return False, "Rate limit exceeded: too many requests per minute"
        
        if bucket["hour_tokens"] <= 0:
            return False, "Rate limit exceeded: too many requests per hour"
        
        # Consume tokens
        bucket["minute_tokens"] -= 1
        bucket["hour_tokens"] -= 1
        
        return True, ""
    
    async def process(
        self,
        request: Dict[str, Any],
        context: MiddlewareContext,
        next_middleware: Callable
    ) -> MiddlewareResult:
        """Check rate limits before processing"""
        salon_id = context.salon_id or "default"
        
        allowed, message = self._check_rate_limit(salon_id)
        
        if not allowed:
            logger.warning(
                "rate_limit_exceeded",
                request_id=context.request_id,
                salon_id=salon_id
            )
            return MiddlewareResult(
                success=False,
                blocked=True,
                message=message
            )
        
        return await next_middleware(request, context)


# Export all middleware
__all__ = [
    "BaseMiddleware",
    "MiddlewareContext",
    "MiddlewareResult",
    "GuardrailMiddleware",
    "CacheMiddleware",
    "ModelRouterMiddleware",
    "LoggingMiddleware",
    "RateLimitMiddleware",
]
