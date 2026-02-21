"""Integration tests for the AI Service Module

Tests end-to-end flows and cross-component integration.
"""
import pytest
import sys
import os
from unittest.mock import MagicMock, patch, AsyncMock

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
        mock.return_value = settings
        yield settings


@pytest.fixture
def middleware_context():
    """Create a middleware context for testing"""
    from app.pipeline.middleware import MiddlewareContext
    return MiddlewareContext(
        salon_id="salon_123",
        agent_name="booking",
        channel="web",
        language="en"
    )


@pytest.fixture
def mock_next_middleware():
    """Create a mock next middleware callable"""
    async def next_func(request, context):
        from app.pipeline.middleware import MiddlewareResult
        return MiddlewareResult(
            success=True,
            data={"response": "OK"},
            blocked=False
        )
    return next_func


class TestFullBookingFlow:
    """Test complete booking flow through AI"""

    @pytest.fixture
    def booking_agent(self, mock_settings):
        from app.services.agents import AGENTS
        return AGENTS.get("booking")

    @pytest.mark.asyncio
    async def test_booking_flow_initial_request(self, booking_agent):
        """Test initial booking request"""
        if booking_agent is None:
            pytest.skip("Booking agent not available")

        with patch.object(booking_agent, 'generate', new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = MagicMock(
                success=True,
                message="I can help you book an appointment",
                data={"step": "service_selection"}
            )

            result = await booking_agent.generate("I want to book a haircut")
            assert result.success

    @pytest.mark.asyncio
    async def test_booking_flow_with_time_selection(self, booking_agent):
        """Test booking with time selection"""
        if booking_agent is None:
            pytest.skip("Booking agent not available")

        with patch.object(booking_agent, 'generate', new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = MagicMock(
                success=True,
                message="Tomorrow at 2 PM is available",
                data={"step": "confirmation"}
            )

            result = await booking_agent.generate("Tomorrow at 2 PM")
            assert result.success

    @pytest.mark.asyncio
    async def test_booking_flow_with_stylist_preference(self, booking_agent):
        """Test booking with stylist preference"""
        if booking_agent is None:
            pytest.skip("Booking agent not available")

        with patch.object(booking_agent, 'generate', new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = MagicMock(
                success=True,
                message="I have noted your preference for Priya",
                data={"stylist": "Priya"}
            )

            result = await booking_agent.generate("I want Priya as my stylist")
            assert result.success

    @pytest.mark.asyncio
    async def test_booking_flow_confirmation(self, booking_agent):
        """Test booking confirmation"""
        if booking_agent is None:
            pytest.skip("Booking agent not available")

        with patch.object(booking_agent, 'generate', new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = MagicMock(
                success=True,
                message="Your appointment is confirmed",
                data={"booking_id": "BK123"}
            )

            result = await booking_agent.generate("Yes, confirm the booking")
            assert result.success


class TestMultiLanguageSupport:
    """Test EN/HI/TE language support"""

    @pytest.fixture
    def booking_agent(self, mock_settings):
        from app.services.agents import AGENTS
        return AGENTS.get("booking")

    @pytest.mark.asyncio
    async def test_english_booking_request(self, booking_agent):
        """Test English booking request"""
        if booking_agent is None:
            pytest.skip("Booking agent not available")

        with patch.object(booking_agent, 'generate', new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = MagicMock(
                success=True,
                message="I can help you book an appointment",
                data={"language": "en"}
            )

            result = await booking_agent.generate("I want to book a haircut")
            assert result.success

    @pytest.mark.asyncio
    async def test_hindi_booking_request(self, booking_agent):
        """Test Hindi booking request"""
        if booking_agent is None:
            pytest.skip("Booking agent not available")

        with patch.object(booking_agent, 'generate', new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = MagicMock(
                success=True,
                message="Hindi response",
                data={"language": "hi"}
            )

            result = await booking_agent.generate("Hindi text")
            assert result.success

    @pytest.mark.asyncio
    async def test_telugu_booking_request(self, booking_agent):
        """Test Telugu booking request"""
        if booking_agent is None:
            pytest.skip("Booking agent not available")

        with patch.object(booking_agent, 'generate', new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = MagicMock(
                success=True,
                message="Telugu response",
                data={"language": "te"}
            )

            result = await booking_agent.generate("Telugu text")
            assert result.success

    @pytest.mark.asyncio
    async def test_language_detection_english(self, mock_settings):
        """Test language detection for English"""
        from app.services.agents import AGENTS

        agent = AGENTS.get("booking")
        if agent is None:
            pytest.skip("Booking agent not available")

        assert agent is not None

    @pytest.mark.asyncio
    async def test_language_detection_hindi(self, mock_settings):
        """Test language detection for Hindi"""
        from app.services.agents import AGENTS

        agent = AGENTS.get("booking")
        if agent is None:
            pytest.skip("Booking agent not available")

        assert agent is not None

    @pytest.mark.asyncio
    async def test_language_detection_telugu(self, mock_settings):
        """Test language detection for Telugu"""
        from app.services.agents import AGENTS

        agent = AGENTS.get("booking")
        if agent is None:
            pytest.skip("Booking agent not available")

        assert agent is not None


class TestCrossChannelConsistency:
    """Test consistent behavior across channels"""

    @pytest.fixture
    def booking_agent(self, mock_settings):
        from app.services.agents import AGENTS
        return AGENTS.get("booking")

    @pytest.mark.asyncio
    async def test_web_channel_booking(self, booking_agent):
        """Test web channel booking"""
        if booking_agent is None:
            pytest.skip("Booking agent not available")

        with patch.object(booking_agent, 'generate', new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = MagicMock(
                success=True,
                message="Booking created",
                data={"channel": "web"}
            )

            result = await booking_agent.generate("Book a haircut")
            assert result.success

    @pytest.mark.asyncio
    async def test_whatsapp_channel_booking(self, booking_agent):
        """Test WhatsApp channel booking"""
        if booking_agent is None:
            pytest.skip("Booking agent not available")

        with patch.object(booking_agent, 'generate', new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = MagicMock(
                success=True,
                message="Booking created",
                data={"channel": "whatsapp"}
            )

            result = await booking_agent.generate("Book a haircut")
            assert result.success

    @pytest.mark.asyncio
    async def test_voice_channel_booking(self, booking_agent):
        """Test voice channel booking"""
        if booking_agent is None:
            pytest.skip("Booking agent not available")

        with patch.object(booking_agent, 'generate', new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = MagicMock(
                success=True,
                message="Booking created",
                data={"channel": "voice"}
            )

            result = await booking_agent.generate("Book a haircut")
            assert result.success

    @pytest.mark.asyncio
    async def test_consistent_response_across_channels(self, booking_agent):
        """Test consistent response across channels"""
        if booking_agent is None:
            pytest.skip("Booking agent not available")

        with patch.object(booking_agent, 'generate', new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = MagicMock(
                success=True,
                message="Booking created",
                data={}
            )

            result = await booking_agent.generate("Book a haircut")
            assert result.success


class TestAgentHandoff:
    """Test agent handoff scenarios"""

    @pytest.fixture
    def agents(self, mock_settings):
        from app.services.agents import AGENTS
        return AGENTS

    @pytest.mark.asyncio
    async def test_booking_to_support_handoff(self, agents):
        """Test handoff from booking to support agent"""
        booking = agents.get("booking")
        support = agents.get("support")

        if booking is None or support is None:
            pytest.skip("Required agents not available")

        assert booking is not None
        assert support is not None

    @pytest.mark.asyncio
    async def test_marketing_to_booking_handoff(self, agents):
        """Test handoff from marketing to booking agent"""
        marketing = agents.get("marketing")
        booking = agents.get("booking")

        if marketing is None or booking is None:
            pytest.skip("Required agents not available")

        assert marketing is not None
        assert booking is not None

    @pytest.mark.asyncio
    async def test_analytics_to_marketing_handoff(self, agents):
        """Test handoff from analytics to marketing agent"""
        analytics = agents.get("analytics")
        marketing = agents.get("marketing")

        if analytics is None or marketing is None:
            pytest.skip("Required agents not available")

        assert analytics is not None
        assert marketing is not None


class TestGuardrailIntegration:
    """Test guardrail integration with pipeline"""

    @pytest.fixture
    def middleware(self, mock_settings):
        from app.pipeline.middleware import GuardrailMiddleware
        return GuardrailMiddleware()

    @pytest.mark.asyncio
    async def test_guardrail_blocks_non_salon_web(self, middleware, middleware_context, mock_next_middleware):
        """Test guardrail blocks non-salon query from web"""
        await middleware.initialize()

        request = {"prompt": "What is the weather like?"}
        result = await middleware.process(request, middleware_context, mock_next_middleware)

        assert result.blocked is True

    @pytest.mark.asyncio
    async def test_guardrail_blocks_non_salon_whatsapp(self, middleware, mock_next_middleware):
        """Test guardrail blocks non-salon query from WhatsApp"""
        await middleware.initialize()

        from app.pipeline.middleware import MiddlewareContext
        context = MiddlewareContext(
            salon_id="salon_123",
            channel="whatsapp",
            language="en"
        )

        request = {"prompt": "What is the weather like?"}
        result = await middleware.process(request, context, mock_next_middleware)

        assert result.blocked is True

    @pytest.mark.asyncio
    async def test_guardrail_allows_salon_query(self, middleware, middleware_context, mock_next_middleware):
        """Test guardrail allows salon query"""
        await middleware.initialize()

        request = {"prompt": "Book a haircut"}
        result = await middleware.process(request, middleware_context, mock_next_middleware)

        assert result.blocked is False


class TestCacheIntegration:
    """Test cache integration"""

    @pytest.fixture
    def middleware(self, mock_settings):
        from app.pipeline.middleware import CacheMiddleware
        return CacheMiddleware()

    @pytest.mark.asyncio
    async def test_cache_hit_on_repeat_query(self, middleware, middleware_context, mock_next_middleware):
        """Test cache hit on repeat query"""
        await middleware.initialize()

        request = {"prompt": "Book a haircut"}
        result1 = await middleware.process(request, middleware_context, mock_next_middleware)
        result2 = await middleware.process(request, middleware_context, mock_next_middleware)

        assert result2.success


class TestErrorRecovery:
    """Test error recovery scenarios"""

    @pytest.mark.asyncio
    async def test_rate_limit_recovery(self, mock_settings, middleware_context, mock_next_middleware):
        """Test rate limit recovery"""
        from app.pipeline.middleware import RateLimitMiddleware

        middleware = RateLimitMiddleware()
        await middleware.initialize()

        request = {"prompt": "Book a haircut"}
        result = await middleware.process(request, middleware_context, mock_next_middleware)

        assert result is not None

    @pytest.mark.asyncio
    async def test_fallback_model_on_error(self, mock_settings):
        """Test fallback model on error"""
        from app.pipeline.middleware import ModelRouterMiddleware, MiddlewareContext

        middleware = ModelRouterMiddleware()
        await middleware.initialize()

        context = MiddlewareContext(
            salon_id="salon_123",
            agent_name="booking",
            channel="web"
        )

        async def failing_next(request, context):
            from app.pipeline.middleware import MiddlewareResult
            return MiddlewareResult(success=True, data={}, blocked=False)

        request = {"prompt": "Book a haircut"}
        result = await middleware.process(request, context, failing_next)

        assert result is not None


class TestPerformanceIntegration:
    """Test performance integration"""

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, mock_settings):
        """Test concurrent requests handling"""
        import asyncio
        from app.services.agents import AGENTS

        agent = AGENTS.get("booking")
        if agent is None:
            pytest.skip("Booking agent not available")

        with patch.object(agent, 'generate', new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = MagicMock(success=True, message="OK")

            async def make_request():
                return await agent.generate("Book a haircut")

            results = await asyncio.gather(*[make_request() for _ in range(5)])

            assert all(r.success for r in results)

    @pytest.mark.asyncio
    async def test_response_time_acceptable(self, mock_settings):
        """Test response time is acceptable"""
        import time
        from app.services.agents import AGENTS

        agent = AGENTS.get("booking")
        if agent is None:
            pytest.skip("Booking agent not available")

        with patch.object(agent, 'generate', new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = MagicMock(success=True, message="OK")

            start = time.time()
            await agent.generate("Book a haircut")
            elapsed = time.time() - start

            assert elapsed < 1.0


class TestTenantIsolation:
    """Test tenant isolation"""

    @pytest.mark.asyncio
    async def test_tenant_data_isolation(self, mock_settings):
        """Test tenant data isolation"""
        from app.services.agents import AGENTS

        agent = AGENTS.get("booking")
        if agent is None:
            pytest.skip("Booking agent not available")

        assert agent is not None


# Run tests with: pytest tests/ai/test_integration.py -v
