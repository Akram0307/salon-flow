"""Tests for Agents Router

Tests for the agent-specific API endpoints.
"""
import pytest
import sys
import os
from unittest.mock import patch, AsyncMock, MagicMock
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
def mock_agent():
    """Mock agent for testing"""
    agent = MagicMock()
    # Waitlist methods - exact names from router
    agent.process_cancellation = AsyncMock(return_value=MagicMock(
        success=True, data={"result": "test"}, metadata={}
    ))
    agent.prioritize_waitlist = AsyncMock(return_value=MagicMock(
        success=True, data={"result": "test"}, metadata={}
    ))
    # Slot optimizer methods
    agent.detect_gaps = AsyncMock(return_value=MagicMock(
        success=True, data={"result": "test"}, metadata={}
    ))
    # Upsell methods - exact name from router
    agent.analyze_upsell_potential = AsyncMock(return_value=MagicMock(
        success=True, data={"result": "test"}, metadata={}
    ))
    # Dynamic pricing methods - exact name from router
    agent.analyze_demand_patterns = AsyncMock(return_value=MagicMock(
        success=True, data={"result": "test"}, metadata={}
    ))
    # Bundle creator methods
    agent.create_bridal_bundle = AsyncMock(return_value=MagicMock(
        success=True, data={"result": "test"}, metadata={}
    ))
    # Inventory methods - exact name from router
    agent.monitor_stock_levels = AsyncMock(return_value=MagicMock(
        success=True, data={"result": "test"}, metadata={}
    ))
    # Staff scheduling methods - exact name from router
    agent.create_weekly_schedule = AsyncMock(return_value=MagicMock(
        success=True, data={"result": "test"}, metadata={}
    ))
    # Customer retention methods - exact name from router
    agent.identify_at_risk_customers = AsyncMock(return_value=MagicMock(
        success=True, data={"result": "test"}, metadata={}
    ))
    return agent


class TestWaitlistEndpoints:
    """Test waitlist agent endpoints"""

    @pytest.mark.asyncio
    async def test_process_waitlist_cancellation(self, mock_settings, mock_agent):
        """Test waitlist cancellation processing"""
        with patch("app.api.agents_router.get_agent", return_value=mock_agent):
            from app.api.agents_router import process_waitlist_cancellation
            from app.schemas.requests import WaitlistProcessRequest

            request = WaitlistProcessRequest(
                salon_id="salon_123",
                cancelled_booking={"id": "booking_1", "time": "10:00"},
                waitlist_entries=[{"id": "wait_1", "user_id": "user_1"}]
            )

            result = await process_waitlist_cancellation(request)
            assert result is not None

    @pytest.mark.asyncio
    async def test_prioritize_waitlist(self, mock_settings, mock_agent):
        """Test waitlist prioritization"""
        with patch("app.api.agents_router.get_agent", return_value=mock_agent):
            from app.api.agents_router import prioritize_waitlist
            from app.schemas.requests import WaitlistPrioritizeRequest

            request = WaitlistPrioritizeRequest(
                salon_id="salon_123",
                service_id="service_1",
                preferred_date="2024-01-15",
                waitlist_entries=[{"id": "wait_1", "user_id": "user_1"}]
            )

            result = await prioritize_waitlist(request)
            assert result is not None


class TestSlotOptimizerEndpoints:
    """Test slot optimizer agent endpoints"""

    @pytest.mark.asyncio
    async def test_detect_schedule_gaps(self, mock_settings, mock_agent):
        """Test gap detection"""
        with patch("app.api.agents_router.get_agent", return_value=mock_agent):
            from app.api.agents_router import detect_schedule_gaps
            from app.schemas.requests import GapDetectionRequest

            request = GapDetectionRequest(
                salon_id="salon_123",
                staff_id="staff_1",
                date="2024-01-15",
                schedule_data={"bookings": [], "hours": {"start": "09:00", "end": "18:00"}}
            )

            result = await detect_schedule_gaps(request)
            assert result is not None


class TestUpsellEndpoints:
    """Test upsell agent endpoints"""

    @pytest.mark.asyncio
    async def test_analyze_upsell_potential(self, mock_settings, mock_agent):
        """Test upsell analysis"""
        with patch("app.api.agents_router.get_agent", return_value=mock_agent):
            from app.api.agents_router import analyze_upsell_potential
            from app.schemas.requests import UpsellAnalysisRequest

            request = UpsellAnalysisRequest(
                salon_id="salon_123",
                customer_id="customer_1",
                current_booking={"service": "haircut"},
                customer_history=[{"service": "haircut", "date": "2024-01-01"}]
            )

            result = await analyze_upsell_potential(request)
            assert result is not None


class TestDynamicPricingEndpoints:
    """Test dynamic pricing agent endpoints"""

    @pytest.mark.asyncio
    async def test_analyze_demand_patterns(self, mock_settings, mock_agent):
        """Test demand analysis"""
        with patch("app.api.agents_router.get_agent", return_value=mock_agent):
            from app.api.agents_router import analyze_demand_patterns
            from app.schemas.requests import DemandAnalysisRequest

            request = DemandAnalysisRequest(
                salon_id="salon_123",
                historical_data={"bookings": [], "trends": {}}
            )

            result = await analyze_demand_patterns(request)
            assert result is not None


class TestBundleCreatorEndpoints:
    """Test bundle creator agent endpoints"""

    @pytest.mark.asyncio
    async def test_create_bridal_bundle(self, mock_settings, mock_agent):
        """Test bridal bundle creation"""
        with patch("app.api.agents_router.get_agent", return_value=mock_agent):
            from app.api.agents_router import create_bridal_bundle
            from app.schemas.requests import BridalBundleRequest

            request = BridalBundleRequest(
                salon_id="salon_123",
                budget_range={"min": 5000, "max": 15000},
                services_count=5,
                preferences={"style": "traditional"}
            )

            result = await create_bridal_bundle(request)
            assert result is not None


class TestInventoryEndpoints:
    """Test inventory agent endpoints"""

    @pytest.mark.asyncio
    async def test_monitor_stock_levels(self, mock_settings, mock_agent):
        """Test stock monitoring"""
        with patch("app.api.agents_router.get_agent", return_value=mock_agent):
            from app.api.agents_router import monitor_stock_levels
            from app.schemas.requests import StockMonitorRequest

            request = StockMonitorRequest(
                salon_id="salon_123",
                inventory_data=[{"id": "item_1", "name": "Shampoo", "quantity": 10}],
                threshold_config={"low": 5, "critical": 2}
            )

            result = await monitor_stock_levels(request)
            assert result is not None


class TestStaffSchedulingEndpoints:
    """Test staff scheduling agent endpoints"""

    @pytest.mark.asyncio
    async def test_create_weekly_schedule(self, mock_settings, mock_agent):
        """Test weekly schedule creation"""
        with patch("app.api.agents_router.get_agent", return_value=mock_agent):
            from app.api.agents_router import create_weekly_schedule
            from app.schemas.requests import WeeklyScheduleRequest

            request = WeeklyScheduleRequest(
                salon_id="salon_123",
                staff_list=[{"id": "staff_1", "name": "John", "skills": ["haircut"]}],
                demand_forecast={"monday": 10, "tuesday": 15},
                constraints={"max_hours": 8, "min_staff": 2}
            )

            result = await create_weekly_schedule(request)
            assert result is not None


class TestCustomerRetentionEndpoints:
    """Test customer retention agent endpoints"""

    @pytest.mark.asyncio
    async def test_identify_at_risk_customers(self, mock_settings, mock_agent):
        """Test at-risk customer identification"""
        with patch("app.api.agents_router.get_agent", return_value=mock_agent):
            from app.api.agents_router import identify_at_risk_customers
            from app.schemas.requests import AtRiskCustomersRequest

            request = AtRiskCustomersRequest(
                salon_id="salon_123",
                customer_data=[{"id": "customer_1", "last_visit": "2024-01-01"}]
            )

            result = await identify_at_risk_customers(request)
            assert result is not None


class TestErrorHandling:
    """Test error handling in endpoints"""

    @pytest.mark.asyncio
    async def test_waitlist_error(self, mock_settings, mock_agent):
        """Test waitlist endpoint error handling"""
        mock_agent.process_cancellation.side_effect = Exception("Test error")

        with patch("app.api.agents_router.get_agent", return_value=mock_agent):
            from fastapi import HTTPException
            from app.api.agents_router import process_waitlist_cancellation
            from app.schemas.requests import WaitlistProcessRequest

            request = WaitlistProcessRequest(
                salon_id="salon_123",
                cancelled_booking={"id": "booking_1"},
                waitlist_entries=[]
            )

            with pytest.raises(Exception):
                await process_waitlist_cancellation(request)


# Run tests with: pytest tests/ai/test_agents_router.py -v
