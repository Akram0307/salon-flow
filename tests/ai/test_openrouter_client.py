"""Tests for OpenRouter Client

Tests for the OpenRouter API client functionality.
"""
import pytest
import sys
import os
from unittest.mock import patch, AsyncMock, MagicMock
import json

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
def mock_httpx_response():
    """Mock httpx response"""
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {
        "id": "test-id",
        "model": "test-model",
        "choices": [
            {"message": {"role": "assistant", "content": "Test response"}}
        ],
        "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
    }
    return response


class TestOpenRouterClient:
    """Test OpenRouter client functionality"""

    @pytest.fixture
    def client(self, mock_settings):
        from app.services.openrouter_client import OpenRouterClient
        return OpenRouterClient()

    @pytest.mark.asyncio
    async def test_chat_success(self, client, mock_httpx_response):
        """Test successful chat request"""
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = MagicMock()
            mock_instance.post = AsyncMock(return_value=mock_httpx_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            result = await client.chat([{"role": "user", "content": "Hello"}])
            assert result is not None

    @pytest.mark.asyncio
    async def test_chat_with_system_prompt(self, client, mock_httpx_response):
        """Test chat with system prompt"""
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = MagicMock()
            mock_instance.post = AsyncMock(return_value=mock_httpx_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            result = await client.chat(
                [{"role": "user", "content": "Hello"}],
                system_prompt="You are a helpful assistant"
            )
            assert result is not None

    @pytest.mark.asyncio
    async def test_chat_with_model_override(self, client, mock_httpx_response):
        """Test chat with model override"""
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = MagicMock()
            mock_instance.post = AsyncMock(return_value=mock_httpx_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            result = await client.chat(
                [{"role": "user", "content": "Hello"}],
                model="custom-model"
            )
            assert result is not None

    @pytest.mark.asyncio
    async def test_chat_with_temperature(self, client, mock_httpx_response):
        """Test chat with temperature override"""
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = MagicMock()
            mock_instance.post = AsyncMock(return_value=mock_httpx_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            result = await client.chat(
                [{"role": "user", "content": "Hello"}],
                temperature=0.5
            )
            assert result is not None

    @pytest.mark.asyncio
    async def test_chat_with_max_tokens(self, client, mock_httpx_response):
        """Test chat with max_tokens override"""
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = MagicMock()
            mock_instance.post = AsyncMock(return_value=mock_httpx_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            result = await client.chat(
                [{"role": "user", "content": "Hello"}],
                max_tokens=2048
            )
            assert result is not None

    @pytest.mark.asyncio
    async def test_chat_error_handling(self, client):
        """Test chat error handling"""
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = MagicMock()
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"
            mock_instance.post = AsyncMock(return_value=mock_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            with pytest.raises(Exception):
                await client.chat([{"role": "user", "content": "Hello"}])

    @pytest.mark.asyncio
    async def test_chat_rate_limit_error(self, client):
        """Test chat rate limit error handling"""
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = MagicMock()
            mock_response = MagicMock()
            mock_response.status_code = 429
            mock_response.text = "Rate limit exceeded"
            mock_instance.post = AsyncMock(return_value=mock_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            with pytest.raises(Exception):
                await client.chat([{"role": "user", "content": "Hello"}])

    @pytest.mark.asyncio
    async def test_chat_timeout_error(self, client):
        """Test chat timeout error handling"""
        import httpx
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = MagicMock()
            mock_instance.post = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            with pytest.raises(Exception):
                await client.chat([{"role": "user", "content": "Hello"}])

    @pytest.mark.asyncio
    async def test_generate_with_context(self, client, mock_httpx_response):
        """Test generate with context"""
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = MagicMock()
            mock_instance.post = AsyncMock(return_value=mock_httpx_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            context = {"salon_id": "salon_123", "user_id": "user_456"}
            result = await client.generate_with_context(
                "Hello",
                context
            )
            assert result is not None

    @pytest.mark.asyncio
    async def test_close(self, client):
        """Test client close"""
        await client.close()

    def test_build_messages(self, client):
        """Test building messages"""
        messages = client._build_messages(
            [{"role": "user", "content": "Hello"}],
            system_prompt="You are helpful"
        )
        assert len(messages) == 2
        assert messages[0]["role"] == "system"

    def test_format_context(self, client):
        """Test formatting context"""
        context = {"salon_id": "salon_123", "user_id": "user_456"}
        result = client._format_context(context)
        assert "salon_id" in result
        assert "user_id" in result


class TestChatMessage:
    """Test ChatMessage model"""

    def test_chat_message_creation(self):
        """Test ChatMessage creation"""
        from app.services.openrouter_client import ChatMessage

        msg = ChatMessage(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"


    def test_chat_message_to_dict(self):
        """Test ChatMessage to_dict"""
        from app.services.openrouter_client import ChatMessage

        msg = ChatMessage(role="user", content="Hello")
        result = msg.to_dict()

        assert result == {"role": "user", "content": "Hello"}


    def test_chat_message_assistant(self):
        """Test ChatMessage for assistant"""
        from app.services.openrouter_client import ChatMessage

        msg = ChatMessage(role="assistant", content="Hi there!")
        assert msg.role == "assistant"
        assert msg.content == "Hi there!"


class TestOpenRouterResponse:
    """Test OpenRouterResponse model"""

    def test_response_creation(self):
        """Test OpenRouterResponse creation"""
        from app.services.openrouter_client import OpenRouterResponse

        response = OpenRouterResponse(
            id="test-id",
            model="test-model",
            choices=[{"message": {"content": "Test"}}],
            usage={"total_tokens": 100}
        )

        assert response.id == "test-id"
        assert response.model == "test-model"


    def test_response_content_extraction(self):
        """Test OpenRouterResponse content extraction"""
        from app.services.openrouter_client import OpenRouterResponse

        response = OpenRouterResponse(
            id="test-id",
            model="test-model",
            choices=[{"message": {"content": "Test response"}}],
            usage={"total_tokens": 100}
        )

        assert response.content == "Test response"


    def test_response_empty_choices(self):
        """Test OpenRouterResponse with empty choices"""
        from app.services.openrouter_client import OpenRouterResponse

        response = OpenRouterResponse(
            id="test-id",
            model="test-model",
            choices=[],
            usage={"total_tokens": 100}
        )

        assert response.content == ""


    def test_response_usage(self):
        """Test OpenRouterResponse usage"""
        from app.services.openrouter_client import OpenRouterResponse

        response = OpenRouterResponse(
            id="test-id",
            model="test-model",
            choices=[{"message": {"content": "Test"}}],
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
        )

        assert response.usage["total_tokens"] == 30


# Run tests with: pytest tests/ai/test_openrouter_client.py -v
