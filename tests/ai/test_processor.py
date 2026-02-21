"""Tests for Pipeline Processor

Tests for the request processing pipeline.
"""
import pytest
import sys
import os
from unittest.mock import patch, AsyncMock, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../services/ai'))


@pytest.fixture(autouse=True)
def mock_settings():
    """Mock settings for all tests"""
    with patch("app.core.config.get_settings") as mock:
        settings = MagicMock()
        settings.openrouter_api_key = "test-api-key"
        settings.openrouter_base_url = "https://openrouter.ai/api/v1"
        settings.openrouter_site_url = "https://salonflow.app"
        settings.openrouter_site_name = "Salon Flow"
        settings.default_model = "google/gemini-2.0-flash-exp:free"
        settings.fallback_model = "google/gemini-flash-1.5"
        settings.max_tokens = 4096
        settings.temperature = 0.7
        settings.redis_url = "redis://localhost:6379/2"
        settings.cache_ttl = 3600
        settings.enable_cache = False
        settings.enable_logging = False
        settings.app_version = "0.1.0"
        settings.upstash_redis_rest_url = None
        settings.upstash_redis_rest_token = None
        mock.return_value = settings
        yield settings


class TestPipelineConfig:
    """Test pipeline configuration"""

    def test_default_config(self):
        """Test default configuration values"""
        from app.pipeline.processor import PipelineConfig

        config = PipelineConfig()
        assert config.enable_guardrail is True
        assert config.enable_cache is True
        assert config.enable_model_router is True
        assert config.enable_logging is True
        assert config.enable_rate_limit is True
        assert config.rate_limit_rpm == 60
        assert config.rate_limit_rph == 1000

    def test_custom_config(self):
        """Test custom configuration values"""
        from app.pipeline.processor import PipelineConfig

        config = PipelineConfig(
            enable_guardrail=False,
            enable_cache=False,
            rate_limit_rpm=120
        )
        assert config.enable_guardrail is False
        assert config.enable_cache is False
        assert config.rate_limit_rpm == 120


class TestRequestProcessor:
    """Test request processor functionality"""

    @pytest.fixture
    def processor(self, mock_settings):
        from app.pipeline.processor import RequestProcessor, PipelineConfig
        config = PipelineConfig(
            enable_cache=False,
            enable_logging=False,
            enable_rate_limit=False
        )
        return RequestProcessor(config=config)



    @pytest.mark.asyncio
    async def test_initialize(self, processor):
        """Test processor initialization"""
        result = await processor.initialize()
        assert result is True
        assert processor._initialized is True


    @pytest.mark.asyncio
    async def test_initialize_idempotent(self, processor):
        """Test initialization is idempotent"""
        result1 = await processor.initialize()
        result2 = await processor.initialize()

        assert result1 is True
        assert result2 is True


    @pytest.mark.asyncio
    async def test_process_request(self, processor):
        """Test processing a request"""
        await processor.initialize()

        with patch.object(processor, 'execute_agent', new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = MagicMock(success=True, data={"response": "test"})

            result = await processor.process(
                request={"prompt": "Book a haircut"},
                context={"salon_id": "salon_123", "agent_name": "booking"}
            )

            assert result is not None


    @pytest.mark.asyncio
    async def test_process_with_guardrail(self, mock_settings):
        """Test processing with guardrail enabled"""
        from app.pipeline.processor import RequestProcessor, PipelineConfig

        config = PipelineConfig(
            enable_guardrail=True,
            enable_cache=False,
            enable_logging=False,
            enable_rate_limit=False,
            enable_model_router=False
        )
        processor = RequestProcessor(config=config)
        await processor.initialize()

        with patch.object(processor, 'execute_agent', new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = MagicMock(success=True, data={"response": "test"})

            result = await processor.process(
                request={"prompt": "Book a haircut"},
                context={"salon_id": "salon_123", "agent_name": "booking"}
            )

            assert result is not None


    @pytest.mark.asyncio
    async def test_process_with_all_middleware(self, mock_settings):
        """Test processing with all middleware enabled"""
        from app.pipeline.processor import RequestProcessor, PipelineConfig

        config = PipelineConfig(
            enable_guardrail=True,
            enable_cache=True,
            enable_logging=True,
            enable_rate_limit=True,
            enable_model_router=True
        )
        processor = RequestProcessor(config=config)

        with patch("app.pipeline.middleware.CacheMiddleware.initialize", new_callable=AsyncMock) as mock_cache_init:
            mock_cache_init.return_value = True
            result = await processor.initialize()
            assert result is True


    @pytest.mark.asyncio
    async def test_cleanup(self, processor):
        """Test processor cleanup"""
        await processor.initialize()
        await processor.cleanup()



    @pytest.mark.asyncio
    async def test_health_check(self, processor):
        """Test health check"""
        await processor.initialize()
        health = await processor.health_check()
        assert health is not None


    @pytest.mark.asyncio
    async def test_execute_agent(self, processor):
        """Test execute_agent method"""
        await processor.initialize()

        with patch("app.services.agents.AGENTS") as mock_agents:
            mock_agent = MagicMock()
            mock_agent.chat = AsyncMock(return_value=MagicMock(success=True, data={"response": "test"}))
            mock_agents.__getitem__ = MagicMock(return_value=mock_agent)
            mock_agents.__contains__ = MagicMock(return_value=True)

            result = await processor.execute_agent(
                agent_name="booking",
                request={"prompt": "Book a haircut"},
                context={"salon_id": "salon_123"}
            )

            assert result is not None


class TestMiddlewareChain:
    """Test middleware chain execution"""

    @pytest.mark.asyncio
    async def test_middleware_count(self, mock_settings):
        """Test middleware count"""
        from app.pipeline.processor import RequestProcessor, PipelineConfig

        config = PipelineConfig(
            enable_guardrail=True,
            enable_cache=False,
            enable_logging=True,
            enable_rate_limit=True,
            enable_model_router=True
        )
        processor = RequestProcessor(config=config)
        await processor.initialize()

        # Check middleware count
        assert len(processor.middlewares) == 4


    @pytest.mark.asyncio
    async def test_middleware_failure_handling(self, mock_settings):
        """Test middleware failure handling"""
        from app.pipeline.processor import RequestProcessor, PipelineConfig
        from app.pipeline.middleware import BaseMiddleware, MiddlewareContext, MiddlewareResult

        class FailingMiddleware(BaseMiddleware):
            name = "failing"

            async def process(self, context: MiddlewareContext) -> MiddlewareResult:
                raise Exception("Middleware failed")

        config = PipelineConfig(
            enable_cache=False,
            enable_logging=False,
            enable_rate_limit=False,
            enable_model_router=False
        )
        processor = RequestProcessor(config=config)
        processor.middlewares = [FailingMiddleware()]
        processor._initialized = True

        result = await processor.process(
            request={"prompt": "test"},
            context={"salon_id": "salon_123"}
        )

        # Should handle failure gracefully
        assert result is not None


# Run tests with: pytest tests/ai/test_processor.py -v
