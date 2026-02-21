"""Request Processor for Pipeline Orchestration

Implements the Pipeline pattern for processing AI requests through
a chain of middleware components.
"""
from typing import Dict, Any, Optional, List, Callable
import structlog
from datetime import datetime

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

logger = structlog.get_logger()


class PipelineConfig:
    """Configuration for the request pipeline"""
    
    def __init__(
        self,
        enable_guardrail: bool = True,
        enable_cache: bool = True,
        enable_model_router: bool = True,
        enable_logging: bool = True,
        enable_rate_limit: bool = True,
        rate_limit_rpm: int = 60,
        rate_limit_rph: int = 1000,
        cache_exact_ttl: int = 3600,
        cache_semantic_ttl: int = 7200,
    ):
        self.enable_guardrail = enable_guardrail
        self.enable_cache = enable_cache
        self.enable_model_router = enable_model_router
        self.enable_logging = enable_logging
        self.enable_rate_limit = enable_rate_limit
        self.rate_limit_rpm = rate_limit_rpm
        self.rate_limit_rph = rate_limit_rph
        self.cache_exact_ttl = cache_exact_ttl
        self.cache_semantic_ttl = cache_semantic_ttl


class RequestProcessor:
    """Pipeline processor for AI requests.
    
    Orchestrates request processing through a chain of middleware:
    1. Logging (request start)
    2. Rate Limiting
    3. Guardrails (salon-only validation)
    4. Cache (exact + semantic)
    5. Model Router (tier-based selection)
    6. Agent Execution
    
    Example:
        processor = RequestProcessor()
        await processor.initialize()
        
        result = await processor.process(
            request={"prompt": "Book a haircut"},
            context={"salon_id": "salon_123", "agent_name": "booking"}
        )
    """
    
    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or PipelineConfig()
        self.middlewares: List[BaseMiddleware] = []
        self._initialized = False
    
    async def initialize(self) -> bool:
        """Initialize all middleware components"""
        if self._initialized:
            return True
        
        # Build middleware chain based on config
        self.middlewares = []
        
        # 1. Logging (always first)
        if self.config.enable_logging:
            self.middlewares.append(LoggingMiddleware())
        
        # 2. Rate Limiting
        if self.config.enable_rate_limit:
            self.middlewares.append(RateLimitMiddleware(
                requests_per_minute=self.config.rate_limit_rpm,
                requests_per_hour=self.config.rate_limit_rph
            ))
        
        # 3. Guardrails
        if self.config.enable_guardrail:
            self.middlewares.append(GuardrailMiddleware())
        
        # 4. Cache
        if self.config.enable_cache:
            self.middlewares.append(CacheMiddleware(
                exact_ttl=self.config.cache_exact_ttl,
                semantic_ttl=self.config.cache_semantic_ttl
            ))
        
        # 5. Model Router
        if self.config.enable_model_router:
            self.middlewares.append(ModelRouterMiddleware())
        
        # Initialize all middleware
        init_results = []
        for middleware in self.middlewares:
            try:
                result = await middleware.initialize()
                init_results.append(result)
                logger.info(
                    "middleware_initialized",
                    name=middleware.name,
                    success=result
                )
            except Exception as e:
                logger.error(
                    "middleware_init_failed",
                    name=middleware.name,
                    error=str(e)
                )
                init_results.append(False)
        
        self._initialized = True
        logger.info(
            "pipeline_initialized",
            middleware_count=len(self.middlewares),
            middleware_names=[m.name for m in self.middlewares]
        )
        
        return all(init_results)
    
    async def process(
        self,
        request: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> MiddlewareResult:
        """Process request through middleware pipeline.
        
        Args:
            request: The request data
            context: Optional context (salon_id, user_id, etc.)
            
        Returns:
            MiddlewareResult with response data
        """
        if not self._initialized:
            await self.initialize()
        
        # Build middleware context
        ctx = MiddlewareContext(
            salon_id=context.get("salon_id") if context else None,
            agent_name=context.get("agent_name") if context else None,
            channel=context.get("channel", "web") if context else "web",
            language=context.get("language", "en") if context else "en",
            user_id=context.get("user_id") if context else None,
            session_id=context.get("session_id") if context else None,
            metadata=context.get("metadata", {}) if context else {}
        )
        
        # Build middleware chain
        chain = self._build_chain(request, ctx)
        
        # Execute chain
        try:
            result = await chain(request, ctx)
            return result
        except Exception as e:
            logger.error(
                "pipeline_execution_error",
                request_id=ctx.request_id,
                error=str(e)
            )
            return MiddlewareResult(
                success=False,
                message=f"Pipeline error: {str(e)}"
            )
    
    def _build_chain(
        self,
        request: Dict[str, Any],
        context: MiddlewareContext
    ) -> Callable:
        """Build the middleware chain.
        
        Returns a callable that executes the chain.
        """
        # Start with the final handler (agent execution)
        async def final_handler(
            req: Dict[str, Any],
            ctx: MiddlewareContext
        ) -> MiddlewareResult:
            # This will be replaced by actual agent execution
            return MiddlewareResult(
                success=True,
                message="Pipeline completed - no agent execution",
                data={"request": req}
            )
        
        chain = final_handler
        
        # Wrap with middleware in reverse order
        for middleware in reversed(self.middlewares):
            chain = self._wrap_middleware(middleware, chain)
        
        return chain
    
    def _wrap_middleware(
        self,
        middleware: BaseMiddleware,
        next_handler: Callable
    ) -> Callable:
        """Wrap a middleware around the next handler."""
        async def wrapper(
            request: Dict[str, Any],
            context: MiddlewareContext
        ) -> MiddlewareResult:
            result = await middleware.process(request, context, next_handler)
            
            # Check if we should skip remaining middleware
            if result.skip_remaining:
                return result
            
            return result
        
        return wrapper
    
    async def execute_agent(
        self,
        agent_name: str,
        request: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> MiddlewareResult:
        """Execute an agent through the pipeline.
        
        Args:
            agent_name: Name of the agent to execute
            request: The request data
            context: Optional context
            
        Returns:
            MiddlewareResult with agent response
        """
        if not self._initialized:
            await self.initialize()
        
        # Add agent name to context
        ctx = context or {}
        ctx["agent_name"] = agent_name
        
        # Process through pipeline
        result = await self.process(request, ctx)
        
        # If pipeline completed without agent execution, execute now
        if result.success and not result.data:
            try:
                from app.plugins import get_registry
                
                registry = get_registry()
                agent_result = await registry.execute(agent_name, request, ctx)
                
                return MiddlewareResult(
                    success=True,
                    data=agent_result,
                    cached=result.cached,
                    metadata=result.metadata
                )
            except Exception as e:
                logger.error(
                    "agent_execution_failed",
                    agent=agent_name,
                    error=str(e)
                )
                return MiddlewareResult(
                    success=False,
                    message=f"Agent execution failed: {str(e)}"
                )
        
        return result
    
    def add_middleware(self, middleware: BaseMiddleware) -> None:
        """Add custom middleware to the pipeline.
        
        Args:
            middleware: Middleware to add
        """
        self.middlewares.append(middleware)
        logger.info("middleware_added", name=middleware.name)
    
    def remove_middleware(self, name: str) -> bool:
        """Remove middleware by name.
        
        Args:
            name: Name of middleware to remove
            
        Returns:
            True if removed, False if not found
        """
        for i, middleware in enumerate(self.middlewares):
            if middleware.name == name:
                self.middlewares.pop(i)
                logger.info("middleware_removed", name=name)
                return True
        return False
    
    async def health_check(self) -> Dict[str, bool]:
        """Check health of all middleware.
        
        Returns:
            Dictionary mapping middleware names to health status
        """
        results = {}
        for middleware in self.middlewares:
            try:
                results[middleware.name] = await middleware.health_check()
            except Exception as e:
                logger.warning(
                    "middleware_health_check_failed",
                    name=middleware.name,
                    error=str(e)
                )
                results[middleware.name] = False
        return results
    
    async def cleanup(self) -> None:
        """Cleanup all middleware resources."""
        for middleware in self.middlewares:
            try:
                await middleware.cleanup()
                logger.info("middleware_cleaned_up", name=middleware.name)
            except Exception as e:
                logger.warning(
                    "middleware_cleanup_failed",
                    name=middleware.name,
                    error=str(e)
                )


# Singleton instance
_processor_instance: Optional[RequestProcessor] = None


def get_processor() -> RequestProcessor:
    """Get or create the singleton processor instance."""
    global _processor_instance
    if _processor_instance is None:
        _processor_instance = RequestProcessor()
    return _processor_instance


async def initialize_pipeline() -> RequestProcessor:
    """Initialize the pipeline and return the processor."""
    processor = get_processor()
    await processor.initialize()
    return processor
