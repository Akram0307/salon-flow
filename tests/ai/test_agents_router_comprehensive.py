"""Comprehensive tests for Agents Router - All 38 endpoints"""
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


@pytest.fixture
def mock_response():
    """Mock AI response"""
    from app.schemas.responses import AIResponse
    return AIResponse(
        success=True,
        message="Operation completed successfully",
        data={"result": "test"},
        confidence=0.9
    )


@pytest.fixture
def mock_waitlist_agent(mock_response):
    """Mock waitlist agent"""
    agent = MagicMock()
    agent.process_cancellation = AsyncMock(return_value=mock_response)
    agent.prioritize_waitlist = AsyncMock(return_value=mock_response)
    agent.generate_notification = AsyncMock(return_value=mock_response)
    agent.handle_escalation = AsyncMock(return_value=mock_response)
    return agent


@pytest.fixture
def mock_slot_optimizer_agent(mock_response):
    """Mock slot optimizer agent"""
    agent = MagicMock()
    agent.detect_gaps = AsyncMock(return_value=mock_response)
    agent.generate_gap_offer = AsyncMock(return_value=mock_response)
    agent.suggest_service_combo = AsyncMock(return_value=mock_response)
    agent.optimize_staff_schedule = AsyncMock(return_value=mock_response)
    return agent


@pytest.fixture
def mock_upsell_agent(mock_response):
    """Mock upsell agent"""
    agent = MagicMock()
    agent.analyze_upsell_potential = AsyncMock(return_value=mock_response)
    agent.suggest_addons = AsyncMock(return_value=mock_response)
    agent.recommend_upgrade = AsyncMock(return_value=mock_response)
    agent.create_combo_offer = AsyncMock(return_value=mock_response)
    agent.track_upsell_success = AsyncMock(return_value=mock_response)
    return agent


@pytest.fixture
def mock_pricing_agent(mock_response):
    """Mock dynamic pricing agent"""
    agent = MagicMock()
    agent.analyze_demand_patterns = AsyncMock(return_value=mock_response)
    agent.suggest_peak_pricing = AsyncMock(return_value=mock_response)
    agent.suggest_offpeak_discounts = AsyncMock(return_value=mock_response)
    agent.analyze_competitor_pricing = AsyncMock(return_value=mock_response)
    agent.suggest_festival_pricing = AsyncMock(return_value=mock_response)
    return agent


@pytest.fixture
def mock_bundle_agent(mock_response):
    """Mock bundle creator agent"""
    agent = MagicMock()
    agent.create_bridal_bundle = AsyncMock(return_value=mock_response)
    agent.create_groom_bundle = AsyncMock(return_value=mock_response)
    agent.create_seasonal_bundle = AsyncMock(return_value=mock_response)
    agent.create_wellness_bundle = AsyncMock(return_value=mock_response)
    agent.suggest_custom_combo = AsyncMock(return_value=mock_response)
    return agent


@pytest.fixture
def mock_inventory_agent(mock_response):
    """Mock inventory agent"""
    agent = MagicMock()
    agent.monitor_stock_levels = AsyncMock(return_value=mock_response)
    agent.predict_reorder_needs = AsyncMock(return_value=mock_response)
    agent.check_expiry_alerts = AsyncMock(return_value=mock_response)
    agent.analyze_usage_patterns = AsyncMock(return_value=mock_response)
    agent.suggest_order_quantities = AsyncMock(return_value=mock_response)
    return agent


@pytest.fixture
def mock_scheduling_agent(mock_response):
    """Mock staff scheduling agent"""
    agent = MagicMock()
    agent.create_weekly_schedule = AsyncMock(return_value=mock_response)
    agent.optimize_shifts = AsyncMock(return_value=mock_response)
    agent.match_skills_to_demand = AsyncMock(return_value=mock_response)
    agent.handle_time_off_request = AsyncMock(return_value=mock_response)
    agent.prevent_overtime = AsyncMock(return_value=mock_response)
    return agent


@pytest.fixture
def mock_retention_agent(mock_response):
    """Mock customer retention agent"""
    agent = MagicMock()
    agent.identify_at_risk_customers = AsyncMock(return_value=mock_response)
    agent.create_winback_campaign = AsyncMock(return_value=mock_response)
    agent.optimize_loyalty_program = AsyncMock(return_value=mock_response)
    agent.create_reengagement_trigger = AsyncMock(return_value=mock_response)
    agent.analyze_churn_factors = AsyncMock(return_value=mock_response)
    return agent


class TestWaitlistEndpoints:
    """Test all waitlist agent endpoints"""

    @pytest.mark.asyncio
    async def test_process_waitlist_cancellation(self, mock_settings, mock_waitlist_agent):
        """Test waitlist cancellation processing"""
        with patch("app.api.agents_router.get_agent", return_value=mock_waitlist_agent):
            from app.api.agents_router import process_waitlist_cancellation
            from app.schemas.requests import WaitlistProcessRequest

            request = WaitlistProcessRequest(
                salon_id="salon_123",
                cancelled_booking={"id": "booking_1", "time": "10:00"},
                waitlist_entries=[{"id": "wait_1", "user_id": "user_1"}]
            )

            result = await process_waitlist_cancellation(request)
            assert result.success is True

    @pytest.mark.asyncio
    async def test_prioritize_waitlist(self, mock_settings, mock_waitlist_agent):
        """Test waitlist prioritization"""
        with patch("app.api.agents_router.get_agent", return_value=mock_waitlist_agent):
            from app.api.agents_router import prioritize_waitlist
            from app.schemas.requests import WaitlistPrioritizeRequest

            request = WaitlistPrioritizeRequest(
                salon_id="salon_123",
                service_id="service_1",
                preferred_date="2024-01-15",
                waitlist_entries=[{"id": "wait_1"}]
            )

            result = await prioritize_waitlist(request)
            assert result.success is True

    @pytest.mark.asyncio
    async def test_generate_waitlist_notification(self, mock_settings, mock_waitlist_agent):
        """Test waitlist notification generation"""
        with patch("app.api.agents_router.get_agent", return_value=mock_waitlist_agent):
            from app.api.agents_router import generate_waitlist_notification
            from app.schemas.requests import WaitlistNotificationRequest

            request = WaitlistNotificationRequest(
                salon_id="salon_123",
                customer_info={"name": "John", "phone": "+1234567890"},
                slot_details={"time": "10:00", "service": "Haircut"},
                response_deadline_minutes=30
            )

            result = await generate_waitlist_notification(request)
            assert result.success is True

    @pytest.mark.asyncio
    async def test_handle_waitlist_escalation(self, mock_settings, mock_waitlist_agent):
        """Test waitlist escalation handling"""
        with patch("app.api.agents_router.get_agent", return_value=mock_waitlist_agent):
            from app.api.agents_router import handle_waitlist_escalation
            from app.schemas.requests import WaitlistEscalationRequest

            request = WaitlistEscalationRequest(
                salon_id="salon_123",
                original_customer={"id": "cust_1"},
                next_candidates=[{"id": "cust_2"}],
                slot_details={"time": "10:00"}
            )

            result = await handle_waitlist_escalation(request)
            assert result.success is True


class TestSlotOptimizerEndpoints:
    """Test all slot optimizer agent endpoints"""

    @pytest.mark.asyncio
    async def test_detect_schedule_gaps(self, mock_settings, mock_slot_optimizer_agent):
        """Test gap detection"""
        with patch("app.api.agents_router.get_agent", return_value=mock_slot_optimizer_agent):
            from app.api.agents_router import detect_schedule_gaps
            from app.schemas.requests import GapDetectionRequest

            request = GapDetectionRequest(
                salon_id="salon_123",
                staff_id="staff_1",
                date="2024-01-15",
                schedule_data={"bookings": [], "hours": {"start": "09:00", "end": "18:00"}}
            )

            result = await detect_schedule_gaps(request)
            assert result.success is True

    @pytest.mark.asyncio
    async def test_generate_gap_offer(self, mock_settings, mock_slot_optimizer_agent):
        """Test gap offer generation"""
        with patch("app.api.agents_router.get_agent", return_value=mock_slot_optimizer_agent):
            from app.api.agents_router import generate_gap_offer
            from app.schemas.requests import GapOfferRequest

            request = GapOfferRequest(
                salon_id="salon_123",
                gap_details={"start": "10:00", "end": "11:00", "duration": 60},
                target_customers=[{"id": "cust_1"}],
                nearby_services=[{"name": "Haircut"}, {"name": "Beard Trim"}]
            )

            result = await generate_gap_offer(request)
            assert result.success is True

    @pytest.mark.asyncio
    async def test_suggest_service_combo(self, mock_settings, mock_slot_optimizer_agent):
        """Test service combo suggestion"""
        with patch("app.api.agents_router.get_agent", return_value=mock_slot_optimizer_agent):
            from app.api.agents_router import suggest_service_combo
            from app.schemas.requests import ServiceComboRequest

            request = ServiceComboRequest(
                salon_id="salon_123",
                gap_duration=60,
                available_services=[{"name": "Haircut"}, {"name": "Spa"}],
                customer_preferences={"style": "modern"}
            )

            result = await suggest_service_combo(request)
            assert result.success is True

    @pytest.mark.asyncio
    async def test_optimize_schedule(self, mock_settings, mock_slot_optimizer_agent):
        """Test schedule optimization"""
        with patch("app.api.agents_router.get_agent", return_value=mock_slot_optimizer_agent):
            from app.api.agents_router import optimize_staff_schedule
            from app.schemas.requests import ScheduleOptimizationRequest

            request = ScheduleOptimizationRequest(
                salon_id="salon_123",
                date="2024-01-15",
                staff_schedules={"staff_1": {"bookings": []}}
            )

            result = await optimize_staff_schedule(request)
            assert result.success is True


class TestUpsellEndpoints:
    """Test all upsell agent endpoints"""

    @pytest.mark.asyncio
    async def test_analyze_upsell_potential(self, mock_settings, mock_upsell_agent):
        """Test upsell analysis"""
        with patch("app.api.agents_router.get_agent", return_value=mock_upsell_agent):
            from app.api.agents_router import analyze_upsell_potential
            from app.schemas.requests import UpsellAnalysisRequest

            request = UpsellAnalysisRequest(
                salon_id="salon_123",
                customer_id="customer_1",
                current_booking={"service": "haircut"},
                customer_history=[{"service": "haircut", "date": "2024-01-01"}]
            )

            result = await analyze_upsell_potential(request)
            assert result.success is True

    @pytest.mark.asyncio
    async def test_suggest_addons(self, mock_settings, mock_upsell_agent):
        """Test addon suggestions"""
        with patch("app.api.agents_router.get_agent", return_value=mock_upsell_agent):
            from app.api.agents_router import suggest_addons
            from app.schemas.requests import AddonSuggestionRequest

            request = AddonSuggestionRequest(
                salon_id="salon_123",
                booked_services=[{"id": "service_1", "name": "Haircut"}],
                available_addons=[{"id": "addon_1", "name": "Beard Trim"}],
                customer_preferences={"style": "modern"}
            )

            result = await suggest_addons(request)
            assert result.success is True

    @pytest.mark.asyncio
    async def test_recommend_upgrade(self, mock_settings, mock_upsell_agent):
        """Test upgrade recommendations"""
        with patch("app.api.agents_router.get_agent", return_value=mock_upsell_agent):
            from app.api.agents_router import recommend_upgrade
            from app.schemas.requests import UpgradeRecommendationRequest

            request = UpgradeRecommendationRequest(
                salon_id="salon_123",
                current_service={"id": "service_1", "name": "Haircut"},
                upgrade_options=[{"name": "Premium Haircut"}, {"name": "Hair Spa"}],
                customer_profile={"tier": "gold", "age": 30}
            )

            result = await recommend_upgrade(request)
            assert result.success is True

    @pytest.mark.asyncio
    async def test_create_combo_offer(self, mock_settings, mock_upsell_agent):
        """Test combo offer creation"""
        with patch("app.api.agents_router.get_agent", return_value=mock_upsell_agent):
            from app.api.agents_router import create_combo_offer
            from app.schemas.requests import ComboOfferRequest

            request = ComboOfferRequest(
                salon_id="salon_123",
                base_services=[{"name": "Haircut"}],
                customer_segment="premium",
                occasion="weekend"
            )

            result = await create_combo_offer(request)
            assert result.success is True

    @pytest.mark.asyncio
    async def test_track_upsell_performance(self, mock_settings, mock_upsell_agent):
        """Test upsell tracking"""
        with patch("app.api.agents_router.get_agent", return_value=mock_upsell_agent):
            from app.api.agents_router import track_upsell_success
            from app.schemas.requests import UpsellTrackingRequest

            request = UpsellTrackingRequest(
                salon_id="salon_123",
                period="week",
                upsell_data=[{"offer": "addon", "conversions": 5}]
            )

            result = await track_upsell_success(request)
            assert result.success is True


class TestDynamicPricingEndpoints:
    """Test all dynamic pricing agent endpoints"""

    @pytest.mark.asyncio
    async def test_analyze_demand_patterns(self, mock_settings, mock_pricing_agent):
        """Test demand analysis"""
        with patch("app.api.agents_router.get_agent", return_value=mock_pricing_agent):
            from app.api.agents_router import analyze_demand_patterns
            from app.schemas.requests import DemandAnalysisRequest

            request = DemandAnalysisRequest(
                salon_id="salon_123",
                historical_data={"bookings": [], "trends": {}}
            )

            result = await analyze_demand_patterns(request)
            assert result.success is True

    @pytest.mark.asyncio
    async def test_calculate_peak_pricing(self, mock_settings, mock_pricing_agent):
        """Test peak pricing calculation"""
        with patch("app.api.agents_router.get_agent", return_value=mock_pricing_agent):
            from app.api.agents_router import suggest_peak_pricing
            from app.schemas.requests import PeakPricingRequest

            request = PeakPricingRequest(
                salon_id="salon_123",
                peak_periods=[{"start": "10:00", "end": "12:00"}],
                current_prices={"haircut": 500},
                demand_forecast={"morning": "high"}
            )

            result = await suggest_peak_pricing(request)
            assert result.success is True

    @pytest.mark.asyncio
    async def test_generate_offpeak_discounts(self, mock_settings, mock_pricing_agent):
        """Test off-peak discount generation"""
        with patch("app.api.agents_router.get_agent", return_value=mock_pricing_agent):
            from app.api.agents_router import suggest_offpeak_discounts
            from app.schemas.requests import OffPeakDiscountRequest

            request = OffPeakDiscountRequest(
                salon_id="salon_123",
                slow_periods=[{"start": "13:00", "end": "15:00"}],
                current_prices={"haircut": 500},
                utilization_data={"afternoon": 30}
            )

            result = await suggest_offpeak_discounts(request)
            assert result.success is True

    @pytest.mark.asyncio
    async def test_analyze_competitor_pricing(self, mock_settings, mock_pricing_agent):
        """Test competitor pricing analysis"""
        with patch("app.api.agents_router.get_agent", return_value=mock_pricing_agent):
            from app.api.agents_router import analyze_competitor_pricing
            from app.schemas.requests import CompetitorPricingRequest

            request = CompetitorPricingRequest(
                salon_id="salon_123",
                competitor_data=[{"name": "Salon A", "price": 600}],
                our_services=[{"name": "Haircut", "price": 500}]
            )

            result = await analyze_competitor_pricing(request)
            assert result.success is True

    @pytest.mark.asyncio
    async def test_create_festival_pricing(self, mock_settings, mock_pricing_agent):
        """Test festival pricing creation"""
        with patch("app.api.agents_router.get_agent", return_value=mock_pricing_agent):
            from app.api.agents_router import suggest_festival_pricing
            from app.schemas.requests import FestivalPricingRequest

            request = FestivalPricingRequest(
                salon_id="salon_123",
                festival="Diwali",
                festival_dates="2024-10-25 to 2024-11-05",
                historical_festival_data={"revenue": 100000}
            )

            result = await suggest_festival_pricing(request)
            assert result.success is True


class TestBundleCreatorEndpoints:
    """Test all bundle creator agent endpoints"""

    @pytest.mark.asyncio
    async def test_create_bridal_bundle(self, mock_settings, mock_bundle_agent):
        """Test bridal bundle creation"""
        with patch("app.api.agents_router.get_agent", return_value=mock_bundle_agent):
            from app.api.agents_router import create_bridal_bundle
            from app.schemas.requests import BridalBundleRequest

            request = BridalBundleRequest(
                salon_id="salon_123",
                budget_range={"min": 5000, "max": 15000},
                services_count=5,
                preferences={"style": "traditional"}
            )

            result = await create_bridal_bundle(request)
            assert result.success is True

    @pytest.mark.asyncio
    async def test_create_groom_bundle(self, mock_settings, mock_bundle_agent):
        """Test groom bundle creation"""
        with patch("app.api.agents_router.get_agent", return_value=mock_bundle_agent):
            from app.api.agents_router import create_groom_bundle
            from app.schemas.requests import GroomBundleRequest

            request = GroomBundleRequest(
                salon_id="salon_123",
                budget_range={"min": 3000, "max": 8000},
                services_count=3,
                preferences={"style": "modern"}
            )

            result = await create_groom_bundle(request)
            assert result.success is True

    @pytest.mark.asyncio
    async def test_create_seasonal_bundle(self, mock_settings, mock_bundle_agent):
        """Test seasonal bundle creation"""
        with patch("app.api.agents_router.get_agent", return_value=mock_bundle_agent):
            from app.api.agents_router import create_seasonal_bundle
            from app.schemas.requests import SeasonalBundleRequest

            request = SeasonalBundleRequest(
                salon_id="salon_123",
                season="summer",
                target_audience="students",
                price_range={"min": 500, "max": 1500}
            )

            result = await create_seasonal_bundle(request)
            assert result.success is True

    @pytest.mark.asyncio
    async def test_create_wellness_bundle(self, mock_settings, mock_bundle_agent):
        """Test wellness bundle creation"""
        with patch("app.api.agents_router.get_agent", return_value=mock_bundle_agent):
            from app.api.agents_router import create_wellness_bundle
            from app.schemas.requests import WellnessBundleRequest

            request = WellnessBundleRequest(
                salon_id="salon_123",
                focus_area="stress_relief",
                duration_minutes=120
            )

            result = await create_wellness_bundle(request)
            assert result.success is True

    @pytest.mark.asyncio
    async def test_suggest_custom_combo(self, mock_settings, mock_bundle_agent):
        """Test custom combo suggestion"""
        with patch("app.api.agents_router.get_agent", return_value=mock_bundle_agent):
            from app.api.agents_router import suggest_custom_combo
            from app.schemas.requests import CustomComboRequest

            request = CustomComboRequest(
                salon_id="salon_123",
                booked_services=["Haircut", "Spa"],
                customer_profile={"budget": 1000},
                available_services=[{"name": "Facial"}, {"name": "Manicure"}]
            )

            result = await suggest_custom_combo(request)
            assert result.success is True


class TestInventoryEndpoints:
    """Test all inventory agent endpoints"""

    @pytest.mark.asyncio
    async def test_monitor_stock_levels(self, mock_settings, mock_inventory_agent):
        """Test stock monitoring"""
        with patch("app.api.agents_router.get_agent", return_value=mock_inventory_agent):
            from app.api.agents_router import monitor_stock_levels
            from app.schemas.requests import StockMonitorRequest

            request = StockMonitorRequest(
                salon_id="salon_123",
                inventory_data=[{"id": "item_1", "name": "Shampoo", "quantity": 10}],
                threshold_config={"low": 5, "critical": 2}
            )

            result = await monitor_stock_levels(request)
            assert result.success is True

    @pytest.mark.asyncio
    async def test_predict_reorder_needs(self, mock_settings, mock_inventory_agent):
        """Test reorder prediction"""
        with patch("app.api.agents_router.get_agent", return_value=mock_inventory_agent):
            from app.api.agents_router import predict_reorder_needs
            from app.schemas.requests import ReorderPredictionRequest

            request = ReorderPredictionRequest(
                salon_id="salon_123",
                usage_history=[{"item": "Shampoo", "daily_usage": 5}],
                current_stock={"Shampoo": 10},
                lead_times={"Shampoo": 7}
            )

            result = await predict_reorder_needs(request)
            assert result.success is True

    @pytest.mark.asyncio
    async def test_check_expiry_alerts(self, mock_settings, mock_inventory_agent):
        """Test expiry alert generation"""
        with patch("app.api.agents_router.get_agent", return_value=mock_inventory_agent):
            from app.api.agents_router import check_expiry_alerts
            from app.schemas.requests import ExpiryAlertRequest

            request = ExpiryAlertRequest(
                salon_id="salon_123",
                inventory_data=[{"id": "item_1", "expiry_date": "2024-03-01"}],
                days_threshold=30
            )

            result = await check_expiry_alerts(request)
            assert result.success is True

    @pytest.mark.asyncio
    async def test_analyze_usage_patterns(self, mock_settings, mock_inventory_agent):
        """Test usage analysis"""
        with patch("app.api.agents_router.get_agent", return_value=mock_inventory_agent):
            from app.api.agents_router import analyze_usage_patterns
            from app.schemas.requests import UsageAnalysisRequest

            request = UsageAnalysisRequest(
                salon_id="salon_123",
                usage_data=[{"item": "Shampoo", "daily_usage": [5, 6, 4]}],
                service_data=[{"name": "Haircut", "products_used": ["Shampoo"]}]
            )

            result = await analyze_usage_patterns(request)
            assert result.success is True

    @pytest.mark.asyncio
    async def test_suggest_order_quantity(self, mock_settings, mock_inventory_agent):
        """Test order quantity suggestion"""
        with patch("app.api.agents_router.get_agent", return_value=mock_inventory_agent):
            from app.api.agents_router import suggest_order_quantity
            from app.schemas.requests import OrderQuantityRequest

            request = OrderQuantityRequest(
                salon_id="salon_123",
                product_id="prod_1",
                product_name="Shampoo",
                usage_rate=5.0,
                current_stock=10,
                lead_time=7
            )

            result = await suggest_order_quantity(request)
            assert result.success is True


class TestStaffSchedulingEndpoints:
    """Test all staff scheduling agent endpoints"""

    @pytest.mark.asyncio
    async def test_create_weekly_schedule(self, mock_settings, mock_scheduling_agent):
        """Test weekly schedule creation"""
        with patch("app.api.agents_router.get_agent", return_value=mock_scheduling_agent):
            from app.api.agents_router import create_weekly_schedule
            from app.schemas.requests import WeeklyScheduleRequest

            request = WeeklyScheduleRequest(
                salon_id="salon_123",
                staff_list=[{"id": "staff_1", "name": "John", "skills": ["haircut"]}],
                demand_forecast={"monday": 10, "tuesday": 15},
                constraints={"max_hours": 8, "min_staff": 2}
            )

            result = await create_weekly_schedule(request)
            assert result.success is True

    @pytest.mark.asyncio
    async def test_optimize_shifts(self, mock_settings, mock_scheduling_agent):
        """Test shift optimization"""
        with patch("app.api.agents_router.get_agent", return_value=mock_scheduling_agent):
            from app.api.agents_router import optimize_shifts
            from app.schemas.requests import ShiftOptimizationRequest

            request = ShiftOptimizationRequest(
                salon_id="salon_123",
                current_schedule={"monday": {"staff_1": "09:00-17:00"}},
                demand_patterns={"morning": 20, "evening": 30},
                staff_preferences=[{"staff_id": "staff_1", "preferred_shift": "morning"}]
            )

            result = await optimize_shifts(request)
            assert result.success is True

    @pytest.mark.asyncio
    async def test_match_skills_to_demand(self, mock_settings, mock_scheduling_agent):
        """Test skill matching"""
        with patch("app.api.agents_router.get_agent", return_value=mock_scheduling_agent):
            from app.api.agents_router import match_skills_to_demand
            from app.schemas.requests import SkillMatchRequest

            request = SkillMatchRequest(
                salon_id="salon_123",
                service_demand=[{"service": "haircut", "count": 10}],
                staff_skills=[{"staff_id": "staff_1", "skills": ["haircut", "coloring"]}]
            )

            result = await match_skills_to_demand(request)
            assert result.success is True

    @pytest.mark.asyncio
    async def test_handle_time_off_request(self, mock_settings, mock_scheduling_agent):
        """Test time off handling"""
        with patch("app.api.agents_router.get_agent", return_value=mock_scheduling_agent):
            from app.api.agents_router import handle_time_off_request
            from app.schemas.requests import TimeOffRequest

            request = TimeOffRequest(
                salon_id="salon_123",
                request={"staff_id": "staff_1", "start": "2024-02-01", "end": "2024-02-03", "reason": "vacation"},
                current_schedule={"bookings": []},
                available_staff=[{"id": "staff_2"}]
            )

            result = await handle_time_off_request(request)
            assert result.success is True

    @pytest.mark.asyncio
    async def test_prevent_overtime(self, mock_settings, mock_scheduling_agent):
        """Test overtime prevention"""
        with patch("app.api.agents_router.get_agent", return_value=mock_scheduling_agent):
            from app.api.agents_router import prevent_overtime
            from app.schemas.requests import OvertimePreventionRequest

            request = OvertimePreventionRequest(
                salon_id="salon_123",
                timesheet_data=[{"staff_id": "staff_1", "hours_worked": 45}],
                max_hours_per_week=40
            )

            result = await prevent_overtime(request)
            assert result.success is True


class TestCustomerRetentionEndpoints:
    """Test all customer retention agent endpoints"""

    @pytest.mark.asyncio
    async def test_identify_at_risk_customers(self, mock_settings, mock_retention_agent):
        """Test at-risk customer identification"""
        with patch("app.api.agents_router.get_agent", return_value=mock_retention_agent):
            from app.api.agents_router import identify_at_risk_customers
            from app.schemas.requests import AtRiskCustomersRequest

            request = AtRiskCustomersRequest(
                salon_id="salon_123",
                customer_data=[{"id": "customer_1", "last_visit": "2024-01-01"}]
            )

            result = await identify_at_risk_customers(request)
            assert result.success is True

    @pytest.mark.asyncio
    async def test_create_winback_campaign(self, mock_settings, mock_retention_agent):
        """Test winback campaign creation"""
        with patch("app.api.agents_router.get_agent", return_value=mock_retention_agent):
            from app.api.agents_router import create_winback_campaign
            from app.schemas.requests import WinbackCampaignRequest

            request = WinbackCampaignRequest(
                salon_id="salon_123",
                customer_segment="inactive",
                last_visit_range="30-60 days",
                offer_budget=5000
            )

            result = await create_winback_campaign(request)
            assert result.success is True

    @pytest.mark.asyncio
    async def test_optimize_loyalty_program(self, mock_settings, mock_retention_agent):
        """Test loyalty program optimization"""
        with patch("app.api.agents_router.get_agent", return_value=mock_retention_agent):
            from app.api.agents_router import optimize_loyalty_program
            from app.schemas.requests import LoyaltyOptimizationRequest

            request = LoyaltyOptimizationRequest(
                salon_id="salon_123",
                loyalty_data={"points_per_rupee": 1, "tiers": []},
                customer_feedback=[{"rating": 4, "comment": "Good"}]
            )

            result = await optimize_loyalty_program(request)
            assert result.success is True

    @pytest.mark.asyncio
    async def test_create_reengagement_trigger(self, mock_settings, mock_retention_agent):
        """Test reengagement trigger creation"""
        with patch("app.api.agents_router.get_agent", return_value=mock_retention_agent):
            from app.api.agents_router import create_reengagement_trigger
            from app.schemas.requests import ReengagementTriggerRequest

            request = ReengagementTriggerRequest(
                salon_id="salon_123",
                customer_profile={"id": "cust_1", "last_visit": "30 days ago"},
                trigger_event="no_visit_30_days"
            )

            result = await create_reengagement_trigger(request)
            assert result.success is True

    @pytest.mark.asyncio
    async def test_analyze_churn_factors(self, mock_settings, mock_retention_agent):
        """Test churn analysis"""
        with patch("app.api.agents_router.get_agent", return_value=mock_retention_agent):
            from app.api.agents_router import analyze_churn_factors
            from app.schemas.requests import ChurnAnalysisRequest

            request = ChurnAnalysisRequest(
                salon_id="salon_123",
                churned_customers=[{"id": "cust_1", "churn_date": "2024-01-01"}],
                active_customers=[{"id": "cust_2"}]
            )

            result = await analyze_churn_factors(request)
            assert result.success is True


class TestErrorHandling:
    """Test error handling in all endpoints"""

    @pytest.mark.asyncio
    async def test_waitlist_error(self, mock_settings, mock_waitlist_agent):
        """Test waitlist endpoint error handling"""
        mock_waitlist_agent.process_cancellation.side_effect = Exception("Test error")

        with patch("app.api.agents_router.get_agent", return_value=mock_waitlist_agent):
            from app.api.agents_router import process_waitlist_cancellation
            from app.schemas.requests import WaitlistProcessRequest

            request = WaitlistProcessRequest(
                salon_id="salon_123",
                cancelled_booking={"id": "booking_1"},
                waitlist_entries=[]
            )

            with pytest.raises(Exception):
                await process_waitlist_cancellation(request)

    @pytest.mark.asyncio
    async def test_slot_optimizer_error(self, mock_settings, mock_slot_optimizer_agent):
        """Test slot optimizer endpoint error handling"""
        mock_slot_optimizer_agent.detect_gaps.side_effect = Exception("Test error")

        with patch("app.api.agents_router.get_agent", return_value=mock_slot_optimizer_agent):
            from app.api.agents_router import detect_schedule_gaps
            from app.schemas.requests import GapDetectionRequest

            request = GapDetectionRequest(
                salon_id="salon_123",
                staff_id="staff_1",
                date="2024-01-15",
                schedule_data={}
            )

            with pytest.raises(Exception):
                await detect_schedule_gaps(request)

    @pytest.mark.asyncio
    async def test_upsell_error(self, mock_settings, mock_upsell_agent):
        """Test upsell endpoint error handling"""
        mock_upsell_agent.analyze_upsell_potential.side_effect = Exception("Test error")

        with patch("app.api.agents_router.get_agent", return_value=mock_upsell_agent):
            from app.api.agents_router import analyze_upsell_potential
            from app.schemas.requests import UpsellAnalysisRequest

            request = UpsellAnalysisRequest(
                salon_id="salon_123",
                customer_id="customer_1",
                current_booking={},
                customer_history=[]
            )

            with pytest.raises(Exception):
                await analyze_upsell_potential(request)

    @pytest.mark.asyncio
    async def test_pricing_error(self, mock_settings, mock_pricing_agent):
        """Test pricing endpoint error handling"""
        mock_pricing_agent.analyze_demand_patterns.side_effect = Exception("Test error")

        with patch("app.api.agents_router.get_agent", return_value=mock_pricing_agent):
            from app.api.agents_router import analyze_demand_patterns
            from app.schemas.requests import DemandAnalysisRequest

            request = DemandAnalysisRequest(
                salon_id="salon_123",
                historical_data={}
            )

            with pytest.raises(Exception):
                await analyze_demand_patterns(request)

    @pytest.mark.asyncio
    async def test_bundle_error(self, mock_settings, mock_bundle_agent):
        """Test bundle endpoint error handling"""
        mock_bundle_agent.create_bridal_bundle.side_effect = Exception("Test error")

        with patch("app.api.agents_router.get_agent", return_value=mock_bundle_agent):
            from app.api.agents_router import create_bridal_bundle
            from app.schemas.requests import BridalBundleRequest

            request = BridalBundleRequest(
                salon_id="salon_123",
                budget_range={"min": 5000, "max": 15000},
                services_count=5,
                preferences={}
            )

            with pytest.raises(Exception):
                await create_bridal_bundle(request)

    @pytest.mark.asyncio
    async def test_inventory_error(self, mock_settings, mock_inventory_agent):
        """Test inventory endpoint error handling"""
        mock_inventory_agent.monitor_stock_levels.side_effect = Exception("Test error")

        with patch("app.api.agents_router.get_agent", return_value=mock_inventory_agent):
            from app.api.agents_router import monitor_stock_levels
            from app.schemas.requests import StockMonitorRequest

            request = StockMonitorRequest(
                salon_id="salon_123",
                inventory_data=[],
                threshold_config={}
            )

            with pytest.raises(Exception):
                await monitor_stock_levels(request)

    @pytest.mark.asyncio
    async def test_scheduling_error(self, mock_settings, mock_scheduling_agent):
        """Test scheduling endpoint error handling"""
        mock_scheduling_agent.create_weekly_schedule.side_effect = Exception("Test error")

        with patch("app.api.agents_router.get_agent", return_value=mock_scheduling_agent):
            from app.api.agents_router import create_weekly_schedule
            from app.schemas.requests import WeeklyScheduleRequest

            request = WeeklyScheduleRequest(
                salon_id="salon_123",
                staff_list=[],
                demand_forecast={},
                constraints={}
            )

            with pytest.raises(Exception):
                await create_weekly_schedule(request)

    @pytest.mark.asyncio
    async def test_retention_error(self, mock_settings, mock_retention_agent):
        """Test retention endpoint error handling"""
        mock_retention_agent.identify_at_risk_customers.side_effect = Exception("Test error")

        with patch("app.api.agents_router.get_agent", return_value=mock_retention_agent):
            from app.api.agents_router import identify_at_risk_customers
            from app.schemas.requests import AtRiskCustomersRequest

            request = AtRiskCustomersRequest(
                salon_id="salon_123",
                customer_data=[]
            )

            with pytest.raises(Exception):
                await identify_at_risk_customers(request)


# Run tests with: pytest tests/ai/test_agents_router_comprehensive.py -v
