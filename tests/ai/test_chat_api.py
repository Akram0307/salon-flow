"""Tests for Chat API endpoints"""
import pytest
import sys
import os
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi import FastAPI
from fastapi.testclient import TestClient

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


@pytest.fixture
def mock_booking_agent():
    """Mock booking agent"""
    from app.schemas.responses import AIResponse

    agent = MagicMock()
    agent.generate = AsyncMock(return_value=AIResponse(
        success=True,
        message="I can help you book an appointment",
        data={},
        confidence=0.9,
        suggestions=["Book haircut", "Check availability"]
    ))
    agent.suggest_time_slots = AsyncMock(return_value=AIResponse(
        success=True,
        message="Here are available slots",
        data={"slots": ["10:00 AM", "2:00 PM", "4:00 PM"]},
        confidence=0.85
    ))
    agent.recommend_stylist = AsyncMock(return_value=AIResponse(
        success=True,
        message="I recommend Priya for your service",
        data={"stylist_id": "stylist-123", "stylist_name": "Priya"},
        confidence=0.9
    ))
    return agent


@pytest.fixture
def mock_generic_agent():
    """Mock generic agent"""
    from app.schemas.responses import AIResponse

    agent = MagicMock()
    agent.generate = AsyncMock(return_value=AIResponse(
        success=True,
        message="Generic response",
        data={},
        confidence=0.75
    ))
    return agent


@pytest.fixture
def app(mock_settings):
    """Create test app"""
    from app.api.chat import router

    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(app, mock_booking_agent, mock_generic_agent):
    """Create test client with mocked get_agent"""
    def mock_get_agent(name):
        if name == "booking":
            return mock_booking_agent
        return mock_generic_agent

    with patch("app.api.chat.get_agent", side_effect=mock_get_agent):
        with TestClient(app) as client:
            yield client


class TestChatEndpoints:
    """Test chat API endpoints"""

    def test_chat_new_session(self, client, mock_generic_agent):
        """Test chat with new session"""
        response = client.post("/chat", json={
            "salon_id": "salon-123",
            "message": "Hello, I want to book an appointment",
            "agent_type": "booking"
        })

        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "session_id" in data
        assert data["agent_type"] == "booking"


    def test_chat_existing_session(self, client, mock_generic_agent):
        """Test chat with existing session"""
        # First message to create session
        response1 = client.post("/chat", json={
            "salon_id": "salon-123",
            "message": "Hello",
            "agent_type": "booking"
        })
        session_id = response1.json()["session_id"]

        # Second message with same session
        response2 = client.post("/chat", json={
            "salon_id": "salon-123",
            "message": "I want a haircut",
            "agent_type": "booking",
            "session_id": session_id
        })

        assert response2.status_code == 200
        data = response2.json()
        assert data["session_id"] == session_id



    def test_chat_with_context(self, client, mock_generic_agent):
        """Test chat with additional context"""
        response = client.post("/chat", json={
            "salon_id": "salon-123",
            "message": "What services do you offer?",
            "agent_type": "booking",
            "context": {"customer_id": "cust-456", "language": "en"}
        })


        assert response.status_code == 200
        data = response.json()
        assert "response" in data



    def test_chat_suggestions_included(self, client, mock_booking_agent):
        """Test chat response includes suggestions"""
        response = client.post("/chat", json={
            "salon_id": "salon-123",
            "message": "I need a haircut",
            "agent_type": "booking"
        })

        assert response.status_code == 200
        data = response.json()
        assert "suggestions" in data


    def test_suggest_booking(self, client, mock_booking_agent):
        """Test booking suggestion endpoint"""
        response = client.post("/chat/booking/suggest", json={
            "salon_id": "salon-123",
            "service_ids": ["service-1", "service-2"],
            "preferred_date": "2024-02-15",
            "preferred_time": "10:00"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        mock_booking_agent.suggest_time_slots.assert_called_once()



    def test_suggest_booking_with_staff_preference(self, client, mock_booking_agent):
        """Test booking suggestion with staff preference"""
        response = client.post("/chat/booking/suggest", json={
            "salon_id": "salon-123",
            "service_ids": ["service-1"],
            "preferred_date": "2024-02-15",
            "preferred_time": "14:00",
            "staff_preference": "stylist-123"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True



    def test_recommend_stylist(self, client, mock_booking_agent):
        """Test stylist recommendation endpoint"""
        response = client.post("/chat/booking/recommend-stylist", json={
            "salon_id": "salon-123",
            "service_ids": ["service-1", "service-2"],
            "customer_preferences": {"experience_level": "senior", "gender_preference": "female"}
        })


        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        mock_booking_agent.recommend_stylist.assert_called_once()



    def test_recommend_stylist_no_preferences(self, client, mock_booking_agent):
        """Test stylist recommendation without preferences"""
        response = client.post("/chat/booking/recommend-stylist", json={
            "salon_id": "salon-123",
            "service_ids": ["service-1"]
        })

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True



    def test_clear_session(self, client):
        """Test clearing session"""
        # Create a session first
        from app.api.chat import sessions
        sessions["test-session-123"] = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi!"}
        ]

        response = client.delete("/chat/session/test-session-123")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "cleared"
        assert data["session_id"] == "test-session-123"



    def test_clear_nonexistent_session(self, client):
        """Test clearing non-existent session"""
        response = client.delete("/chat/session/nonexistent-session")


        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "cleared"



    def test_chat_error(self, client, mock_booking_agent):
        """Test chat error handling"""
        mock_booking_agent.generate.side_effect = Exception("Test error")

        response = client.post("/chat", json={
            "salon_id": "salon-123",
            "message": "Hello",
            "agent_type": "booking"
        })

        assert response.status_code == 500



    def test_suggest_booking_error(self, client, mock_booking_agent):
        """Test booking suggestion error handling"""
        mock_booking_agent.suggest_time_slots.side_effect = Exception("Test error")

        response = client.post("/chat/booking/suggest", json={
            "salon_id": "salon-123",
            "service_ids": ["service-1"],
            "preferred_date": "2024-02-15"
        })

        assert response.status_code == 500



    def test_recommend_stylist_error(self, client, mock_booking_agent):
        """Test stylist recommendation error handling"""
        mock_booking_agent.recommend_stylist.side_effect = Exception("Test error")

        response = client.post("/chat/booking/recommend-stylist", json={
            "salon_id": "salon-123",
            "service_ids": ["service-1"]
        })

        assert response.status_code == 500


# Run tests with: pytest tests/ai/test_chat_api.py -v
