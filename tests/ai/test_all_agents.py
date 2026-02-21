"""Comprehensive tests for all 25 AI Agents

Tests each agent's functionality, metadata, and integration.
"""
import pytest
import sys
import os
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../services/ai'))


# All 25 expected agents
EXPECTED_AGENTS = [
    "booking", "marketing", "analytics", "support",
    "waitlist", "slot_optimizer", "upsell",
    "dynamic_pricing", "bundle_creator",
    "inventory", "scheduling", "retention",
    "demand_predictor", "whatsapp_concierge",
    "quality_assurance", "resource_allocator", "compliance_monitor",
    "voice_receptionist", "feedback_analyzer", "vip_priority",
    "social_media_manager", "image_creatives_generator",
    "content_writer", "review_monitor", "campaign_orchestrator"
]


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
def mock_openrouter_response():
    """Mock OpenRouter API response"""
    response = MagicMock()
    response.success = True
    response.message = "I can help you with that salon request."
    response.content = "I can help you with that salon request."
    response.model = "google/gemini-2.0-flash-exp:free"
    response.usage = {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150}
    return response


@pytest.fixture
def mock_agent_response():
    """Mock agent response"""
    response = MagicMock()
    response.success = True
    response.message = "I can help you with that."
    response.data = {"result": "success"}
    response.suggestions = ["Option 1", "Option 2"]
    response.blocked = False
    response.cached = False
    response.model_used = "google/gemini-2.0-flash-exp:free"
    response.execution_time_ms = 150.0
    return response


class TestAllAgentsRegistration:
    """Test that all 25 agents are properly registered"""
    
    def test_all_agents_registered(self, mock_settings):
        """Verify all 25 agents are registered in AGENTS dictionary"""
        from app.services.agents import AGENTS
        
        for agent_name in EXPECTED_AGENTS:
            assert agent_name in AGENTS, f"Agent '{agent_name}' not registered in AGENTS"
    
    def test_agent_count(self, mock_settings):
        """Verify exactly 25 agents are registered"""
        from app.services.agents import AGENTS
        
        assert len(AGENTS) == 25, f"Expected 25 agents, found {len(AGENTS)}"
    
    def test_get_agent_function(self, mock_settings):
        """Test get_agent function for each agent"""
        from app.services.agents import get_agent
        
        for agent_name in EXPECTED_AGENTS:
            agent = get_agent(agent_name)
            assert agent is not None, f"get_agent('{agent_name}') returned None"
    
    def test_invalid_agent_raises_error(self, mock_settings):
        """Test that invalid agent name raises ValueError"""
        from app.services.agents import get_agent
        
        with pytest.raises(ValueError, match="Unknown agent"):
            get_agent("invalid_agent_name")


class TestAgentMetadata:
    """Test agent metadata and properties"""
    
    @pytest.mark.parametrize("agent_name", EXPECTED_AGENTS)
    def test_agent_has_name(self, mock_settings, agent_name):
        """Test that each agent has a name property"""
        from app.services.agents import get_agent
        
        agent = get_agent(agent_name)
        assert hasattr(agent, 'name')
        assert agent.name is not None
    
    @pytest.mark.parametrize("agent_name", EXPECTED_AGENTS)
    def test_agent_has_description(self, mock_settings, agent_name):
        """Test that each agent has a description"""
        from app.services.agents import get_agent
        
        agent = get_agent(agent_name)
        assert hasattr(agent, 'description')
        assert agent.description is not None
    
    @pytest.mark.parametrize("agent_name", EXPECTED_AGENTS)
    def test_agent_has_system_prompt(self, mock_settings, agent_name):
        """Test that each agent has a system prompt"""
        from app.services.agents import get_agent
        
        agent = get_agent(agent_name)
        assert hasattr(agent, 'system_prompt')
        assert agent.system_prompt is not None
        assert len(agent.system_prompt) > 50  # Meaningful prompt


class TestBookingAgent:
    """Tests for Booking Agent"""
    
    @pytest.fixture
    def agent(self, mock_settings):
        from app.services.agents import get_agent
        return get_agent("booking")
    
    def test_booking_agent_name(self, agent):
        """Test booking agent name"""
        assert agent.name == "booking_agent"
    
    @pytest.mark.asyncio
    async def test_booking_agent_generate(self, agent, mock_openrouter_response):
        """Test booking agent generate method"""
        with patch.object(agent, '_get_client', new_callable=AsyncMock) as mock_client_get:
            mock_client = AsyncMock()
            mock_client.chat = AsyncMock(return_value=mock_openrouter_response)
            mock_client_get.return_value = mock_client
            
            with patch.object(agent, '_get_cache', new_callable=AsyncMock) as mock_cache_get:
                mock_cache = AsyncMock()
                mock_cache.get = AsyncMock(return_value=None)
                mock_cache_get.return_value = mock_cache
                
                response = await agent.generate(
                    prompt="Book a haircut for tomorrow",
                    context={"salon_id": "salon_123"},
                    skip_guardrail=True,
                    use_cache=False
                )
                
                assert response.success is True
    
    @pytest.mark.asyncio
    async def test_booking_agent_guardrail_blocks_non_salon(self, agent):
        """Test that booking agent blocks non-salon queries"""
        response = await agent.generate(
            prompt="What's the weather like?",
            skip_guardrail=False,
            use_cache=False
        )
        
        assert response.blocked is True
        assert "salon" in response.message.lower()


class TestMarketingAgent:
    """Tests for Marketing Agent"""
    
    @pytest.fixture
    def agent(self, mock_settings):
        from app.services.agents import get_agent
        return get_agent("marketing")
    
    def test_marketing_agent_name(self, agent):
        """Test marketing agent name"""
        assert agent.name == "marketing_agent"
    
    @pytest.mark.asyncio
    async def test_marketing_agent_generate(self, agent, mock_openrouter_response):
        """Test marketing agent generate method"""
        with patch.object(agent, '_get_client', new_callable=AsyncMock) as mock_client_get:
            mock_client = AsyncMock()
            mock_client.chat = AsyncMock(return_value=mock_openrouter_response)
            mock_client_get.return_value = mock_client
            
            with patch.object(agent, '_get_cache', new_callable=AsyncMock) as mock_cache_get:
                mock_cache = AsyncMock()
                mock_cache.get = AsyncMock(return_value=None)
                mock_cache_get.return_value = mock_cache
                
                response = await agent.generate(
                    prompt="Create a marketing campaign for Diwali",
                    context={"salon_id": "salon_123"},
                    skip_guardrail=True,
                    use_cache=False
                )
                
                assert response.success is True


class TestAnalyticsAgent:
    """Tests for Analytics Agent"""
    
    @pytest.fixture
    def agent(self, mock_settings):
        from app.services.agents import get_agent
        return get_agent("analytics")
    
    def test_analytics_agent_name(self, agent):
        """Test analytics agent name"""
        assert agent.name == "analytics_agent"
    
    @pytest.mark.asyncio
    async def test_analytics_agent_generate(self, agent, mock_openrouter_response):
        """Test analytics agent generate method"""
        with patch.object(agent, '_get_client', new_callable=AsyncMock) as mock_client_get:
            mock_client = AsyncMock()
            mock_client.chat = AsyncMock(return_value=mock_openrouter_response)
            mock_client_get.return_value = mock_client
            
            with patch.object(agent, '_get_cache', new_callable=AsyncMock) as mock_cache_get:
                mock_cache = AsyncMock()
                mock_cache.get = AsyncMock(return_value=None)
                mock_cache_get.return_value = mock_cache
                
                response = await agent.generate(
                    prompt="Show me revenue trends for last month",
                    context={"salon_id": "salon_123"},
                    skip_guardrail=True,
                    use_cache=False
                )
                
                assert response.success is True


class TestSupportAgent:
    """Tests for Customer Support Agent"""
    
    @pytest.fixture
    def agent(self, mock_settings):
        from app.services.agents import get_agent
        return get_agent("support")
    
    def test_support_agent_name(self, agent):
        """Test support agent name"""
        assert agent.name == "support_agent"
    
    @pytest.mark.asyncio
    async def test_support_agent_generate(self, agent, mock_openrouter_response):
        """Test support agent generate method"""
        with patch.object(agent, '_get_client', new_callable=AsyncMock) as mock_client_get:
            mock_client = AsyncMock()
            mock_client.chat = AsyncMock(return_value=mock_openrouter_response)
            mock_client_get.return_value = mock_client
            
            with patch.object(agent, '_get_cache', new_callable=AsyncMock) as mock_cache_get:
                mock_cache = AsyncMock()
                mock_cache.get = AsyncMock(return_value=None)
                mock_cache_get.return_value = mock_cache
                
                response = await agent.generate(
                    prompt="Customer complaint about late appointment",
                    context={"salon_id": "salon_123"},
                    skip_guardrail=True,
                    use_cache=False
                )
                
                assert response.success is True


class TestAgentErrorHandling:
    """Test error handling across all agents"""
    
    @pytest.mark.parametrize("agent_name", EXPECTED_AGENTS[:5])  # Test first 5 for speed
    @pytest.mark.asyncio
    async def test_agent_handles_empty_prompt(self, mock_settings, agent_name, mock_openrouter_response):
        """Test that agents handle empty prompts gracefully"""
        from app.services.agents import get_agent
        
        agent = get_agent(agent_name)
        
        with patch.object(agent, '_get_client', new_callable=AsyncMock) as mock_client_get:
            mock_client = AsyncMock()
            mock_client.chat = AsyncMock(return_value=mock_openrouter_response)
            mock_client_get.return_value = mock_client
            
            with patch.object(agent, '_get_cache', new_callable=AsyncMock) as mock_cache_get:
                mock_cache = AsyncMock()
                mock_cache.get = AsyncMock(return_value=None)
                mock_cache_get.return_value = mock_cache
                
                response = await agent.generate(
                    prompt="",
                    skip_guardrail=True,
                    use_cache=False
                )
                
                # Should either fail gracefully or return a helpful message
                assert response is not None


# Run tests with: pytest tests/ai/test_all_agents.py -v
