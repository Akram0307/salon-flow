"""Tests for AI Service"""
import pytest
import sys
import os
from unittest.mock import AsyncMock, MagicMock, patch

# Add AI service to path
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


class TestOpenRouterClient:
    """Tests for OpenRouter client"""
    
    @pytest.mark.asyncio
    async def test_chat_success(self, mock_settings):
        """Test successful chat completion"""
        from app.services.openrouter_client import OpenRouterClient
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "id": "chatcmpl-123",
            "model": "google/gemini-2.0-flash-exp:free",
            "choices": [{
                "message": {"role": "assistant", "content": "I recommend booking at 2 PM."},
                "finish_reason": "stop"
            }],
            "usage": {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150}
        }
        mock_response.raise_for_status = MagicMock()
        
        mock_httpx = AsyncMock()
        mock_httpx.post = AsyncMock(return_value=mock_response)
        mock_httpx.is_closed = False
        
        client = OpenRouterClient(api_key="test-key")
        client._client = mock_httpx
        
        result = await client.chat("Hello, I need a haircut")
        
        assert result.content == "I recommend booking at 2 PM."
        assert result.model == "google/gemini-2.0-flash-exp:free"
    
    def test_build_messages(self, mock_settings):
        """Test message building"""
        from app.services.openrouter_client import OpenRouterClient, ChatMessage
        
        client = OpenRouterClient(api_key="test-key")
        
        messages = client._build_messages(
            prompt="I need a haircut",
            system_prompt="You are a salon assistant.",
            history=[ChatMessage(role="user", content="Hello")]
        )
        
        assert len(messages) == 3
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"
        assert messages[2]["role"] == "user"


class TestCacheService:
    """Tests for cache service"""
    
    def test_cache_key_generation(self, mock_settings):
        """Test cache key generation"""
        from app.services.cache_service import CacheService
        
        cache = CacheService()
        key1 = cache._generate_key("test", {"a": 1, "b": 2})
        key2 = cache._generate_key("test", {"b": 2, "a": 1})
        
        assert key1 == key2
    
    @pytest.mark.asyncio
    async def test_cache_disabled(self, mock_settings):
        """Test cache when disabled"""
        from app.services.cache_service import CacheService
        
        cache = CacheService()
        cache._enabled = False
        
        result = await cache.get("test-key")
        assert result is None


class TestAgents:
    """Tests for AI agents"""
    
    def test_get_agent_booking(self, mock_settings):
        """Test getting booking agent"""
        from app.services.agents import get_agent, BookingAgent
        
        agent = get_agent("booking")
        assert isinstance(agent, BookingAgent)
        assert agent.name == "booking_agent"
    
    def test_get_agent_marketing(self, mock_settings):
        """Test getting marketing agent"""
        from app.services.agents import get_agent, MarketingAgent
        
        agent = get_agent("marketing")
        assert isinstance(agent, MarketingAgent)
        assert agent.name == "marketing_agent"
    
    def test_get_agent_analytics(self, mock_settings):
        """Test getting analytics agent"""
        from app.services.agents import get_agent, AnalyticsAgent
        
        agent = get_agent("analytics")
        assert isinstance(agent, AnalyticsAgent)
        assert agent.name == "analytics_agent"
    
    def test_get_agent_support(self, mock_settings):
        """Test getting support agent"""
        from app.services.agents import get_agent, CustomerSupportAgent
        
        agent = get_agent("support")
        assert isinstance(agent, CustomerSupportAgent)
        assert agent.name == "support_agent"
    
    def test_get_agent_invalid(self, mock_settings):
        """Test getting invalid agent"""
        from app.services.agents import get_agent
        
        with pytest.raises(ValueError):
            get_agent("invalid_agent")


class TestSchemas:
    """Tests for request/response schemas"""
    
    def test_chat_request_valid(self, mock_settings):
        """Test valid chat request"""
        from app.schemas.requests import ChatRequest
        
        request = ChatRequest(
            message="I need a haircut",
            salon_id="salon-123",
            agent_type="booking"
        )
        
        assert request.message == "I need a haircut"
        assert request.salon_id == "salon-123"
        assert request.agent_type == "booking"
    
    def test_booking_suggestion_request(self, mock_settings):
        """Test booking suggestion request"""
        from app.schemas.requests import BookingSuggestionRequest
        
        request = BookingSuggestionRequest(
            salon_id="salon-123",
            service_ids=["service-1", "service-2"],
            preferred_date="2024-02-20",
            preferred_time="14:00"
        )
        
        assert request.salon_id == "salon-123"
        assert len(request.service_ids) == 2
    
    def test_ai_response(self, mock_settings):
        """Test AI response schema"""
        from app.schemas.responses import AIResponse
        
        response = AIResponse(
            success=True,
            message="Booking confirmed",
            suggestions=["Add hair spa", "Try our new color"]
        )
        
        assert response.success
        assert len(response.suggestions) == 2


class TestAPIEndpoints:
    """Tests for API endpoints"""
    
    def test_health_endpoint(self, mock_settings):
        """Test health check endpoint"""
        from fastapi.testclient import TestClient
        from main import app
        
        client = TestClient(app)
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "service" in data
        assert data["service"] == "ai-service"
    
    def test_models_endpoint(self, mock_settings):
        """Test models listing endpoint"""
        from fastapi.testclient import TestClient
        from main import app
        
        client = TestClient(app)
        response = client.get("/models")
        
        assert response.status_code == 200
        data = response.json()
        assert "default" in data
        assert "available" in data
    
    def test_agents_endpoint(self, mock_settings):
        """Test agents listing endpoint"""
        from fastapi.testclient import TestClient
        from main import app
        
        client = TestClient(app)
        response = client.get("/agents")
        
        assert response.status_code == 200
        data = response.json()
        assert "agents" in data
        assert len(data["agents"]) == 4
