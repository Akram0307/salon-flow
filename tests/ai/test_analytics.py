"""Tests for Analytics API endpoints"""
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
def mock_analytics_agent():
    """Mock analytics agent"""
    from app.schemas.responses import AIResponse

    agent = MagicMock()
    agent.analyze_revenue = AsyncMock(return_value=AIResponse(
        success=True,
        message="Revenue analysis complete",
        data={"total": 10000, "growth": 15},
        confidence=0.9
    ))
    agent.analyze_staff_performance = AsyncMock(return_value=AIResponse(
        success=True,
        message="Staff performance analysis complete",
        data={"staff_id": "123", "rating": 4.5},
        confidence=0.85
    ))
    agent.predict_demand = AsyncMock(return_value=AIResponse(
        success=True,
        message="Demand prediction complete",
        data={"predicted": 50, "category": "haircuts"},
        confidence=0.8
    ))
    agent.generate = AsyncMock(return_value=AIResponse(
        success=True,
        message="Generated response",
        data={},
        confidence=0.75
    ))
    return agent


@pytest.fixture
def mock_support_agent():
    """Mock support agent"""
    from app.schemas.responses import AIResponse

    agent = MagicMock()
    agent.handle_complaint = AsyncMock(return_value=AIResponse(
        success=True,
        message="Complaint handled successfully",
        data={"resolution": "refund"},
        confidence=0.9
    ))
    return agent


@pytest.fixture
def app(mock_settings, mock_analytics_agent, mock_support_agent):
    """Create test app"""
    from app.api.analytics import router

    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(app, mock_analytics_agent, mock_support_agent):
    """Create test client with mocked get_agent"""
    def mock_get_agent(name):
        if name == "analytics":
            return mock_analytics_agent
        elif name == "support":
            return mock_support_agent
        return MagicMock()

    with patch("app.api.analytics.get_agent", side_effect=mock_get_agent):
        with TestClient(app) as client:
            yield client


class TestAnalyticsEndpoints:
    """Test analytics API endpoints"""

    def test_analyze_revenue(self, client, mock_analytics_agent):
        """Test revenue analysis endpoint"""
        response = client.post("/analytics", json={
            "salon_id": "salon-123",
            "analysis_type": "revenue",
            "period": "month",
            "filters": {"category": "haircuts"}
        })

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        mock_analytics_agent.analyze_revenue.assert_called_once()


    def test_analyze_staff(self, client, mock_analytics_agent):
        """Test staff performance analysis endpoint"""
        response = client.post("/analytics", json={
            "salon_id": "salon-123",
            "analysis_type": "staff",
            "period": "month",
            "filters": {"staff_id": "staff-456"}
        })

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        mock_analytics_agent.analyze_staff_performance.assert_called_once()



    def test_analyze_demand(self, client, mock_analytics_agent):
        """Test demand prediction endpoint"""
        response = client.post("/analytics", json={
            "salon_id": "salon-123",
            "analysis_type": "demand",
            "period": "month",
            "filters": {"category": "haircuts"}
        })

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        mock_analytics_agent.predict_demand.assert_called_once()



    def test_analyze_other_type(self, client, mock_analytics_agent):
        """Test other analysis type endpoint"""
        response = client.post("/analytics", json={
            "salon_id": "salon-123",
            "analysis_type": "custom",
            "period": "month",
            "filters": {"custom_field": "value"}
        })

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        mock_analytics_agent.generate.assert_called_once()



    def test_analyze_no_filters(self, client, mock_analytics_agent):
        """Test analysis without filters"""
        response = client.post("/analytics", json={
            "salon_id": "salon-123",
            "analysis_type": "revenue",
            "period": "month"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True



    def test_get_insights(self, client, mock_analytics_agent):
        """Test get insights endpoint"""
        response = client.get("/analytics/insights/salon-123?insight_type=revenue&period=month")

        assert response.status_code == 200
        data = response.json()
        assert data["salon_id"] == "salon-123"
        assert data["insight_type"] == "revenue"
        assert data["period"] == "month"
        assert "insights" in data
        mock_analytics_agent.generate.assert_called_once()



    def test_get_insights_default_params(self, client, mock_analytics_agent):
        """Test get insights with default params"""
        response = client.get("/analytics/insights/salon-123")

        assert response.status_code == 200
        data = response.json()
        assert data["insight_type"] == "general"
        assert data["period"] == "month"



    def test_handle_complaint(self, client, mock_support_agent):
        """Test handle complaint endpoint"""
        response = client.post("/analytics/complaint", json={
            "salon_id": "salon-123",
            "customer_id": "cust-456",
            "complaint": "Service was poor",
            "booking_id": "booking-789"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        mock_support_agent.handle_complaint.assert_called_once()



    def test_handle_complaint_no_booking(self, client, mock_support_agent):
        """Test handle complaint without booking ID"""
        response = client.post("/analytics/complaint", json={
            "salon_id": "salon-123",
            "customer_id": "cust-456",
            "complaint": "Service was poor"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True



    def test_get_recommendations(self, client, mock_analytics_agent):
        """Test get recommendations endpoint"""
        response = client.get("/analytics/recommendations/salon-123")

        assert response.status_code == 200
        data = response.json()
        assert data["salon_id"] == "salon-123"
        assert "recommendations" in data
        mock_analytics_agent.generate.assert_called_once()



    def test_analyze_error(self, client, mock_analytics_agent):
        """Test analyze endpoint error handling"""
        mock_analytics_agent.analyze_revenue.side_effect = Exception("Test error")

        response = client.post("/analytics", json={
            "salon_id": "salon-123",
            "analysis_type": "revenue",
            "period": "month"
        })

        assert response.status_code == 500



    def test_get_insights_error(self, client, mock_analytics_agent):
        """Test get insights error handling"""
        mock_analytics_agent.generate.side_effect = Exception("Test error")

        response = client.get("/analytics/insights/salon-123")

        assert response.status_code == 500



    def test_handle_complaint_error(self, client, mock_support_agent):
        """Test handle complaint error handling"""
        mock_support_agent.handle_complaint.side_effect = Exception("Test error")

        response = client.post("/analytics/complaint", json={
            "salon_id": "salon-123",
            "customer_id": "cust-456",
            "complaint": "Service was poor"
        })

        assert response.status_code == 500



    def test_get_recommendations_error(self, client, mock_analytics_agent):
        """Test get recommendations error handling"""
        mock_analytics_agent.generate.side_effect = Exception("Test error")

        response = client.get("/analytics/recommendations/salon-123")

        assert response.status_code == 500


# Run tests with: pytest tests/ai/test_analytics.py -v
