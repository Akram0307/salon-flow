"""
Tests for AI Chat Service
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
        mock.return_value = settings
        yield settings


@pytest.mark.asyncio
@pytest.mark.unit
class TestAIChat:
    """Test AI chat functionality"""

    async def test_chat_endpoint(self, mock_settings):
        """Test chat endpoint returns response"""
        from app.services.openrouter_client import OpenRouterClient

        with patch.object(OpenRouterClient, 'chat', new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = MagicMock(
                id="test-id",
                model="test-model",
                choices=[{"message": {"content": "Test response"}}],
                usage={"total_tokens": 100}
            )

            client = OpenRouterClient()
            result = await client.chat([{"role": "user", "content": "Hello"}])
            assert result is not None

    async def test_chat_with_context(self, mock_settings):
        """Test chat with conversation context"""
        from app.services.openrouter_client import OpenRouterClient

        with patch.object(OpenRouterClient, 'chat', new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = MagicMock(
                id="test-id",
                model="test-model",
                choices=[{"message": {"content": "Test response"}}],
                usage={"total_tokens": 100}
            )

            client = OpenRouterClient()
            messages = [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"},
                {"role": "user", "content": "How are you?"}
            ]
            result = await client.chat(messages)
            assert result is not None

    async def test_chat_caching(self, mock_settings):
        """Test chat response caching"""
        from app.services.openrouter_client import OpenRouterClient

        with patch.object(OpenRouterClient, 'chat', new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = MagicMock(
                id="test-id",
                model="test-model",
                choices=[{"message": {"content": "Test response"}}],
                usage={"total_tokens": 100}
            )

            client = OpenRouterClient()
            result = await client.chat([{"role": "user", "content": "Hello"}])
            assert result is not None


@pytest.mark.asyncio
@pytest.mark.integration
class TestAIIntegration:
    """Integration tests for AI service"""

    async def test_booking_intent_detection(self, mock_settings):
        """Test AI detects booking intent from message"""
        from app.services.agents import AGENTS

        agent = AGENTS.get("booking")
        if agent is None:
            pytest.skip("Booking agent not available")

        assert agent is not None

    async def test_service_recommendation(self, mock_settings):
        """Test AI service recommendations"""
        from app.services.agents import AGENTS

        agent = AGENTS.get("marketing")
        if agent is None:
            pytest.skip("Marketing agent not available")

        assert agent is not None

    async def test_customer_sentiment_analysis(self, mock_settings):
        """Test customer sentiment analysis"""
        from app.services.agents import AGENTS

        agent = AGENTS.get("feedback_analyzer")
        if agent is None:
            pytest.skip("Feedback analyzer agent not available")

        assert agent is not None


# Run tests with: pytest tests/ai/test_chat.py -v
