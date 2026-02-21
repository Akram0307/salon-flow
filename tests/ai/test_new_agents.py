"""Unit tests for all specialized AI agents

Tests for:
- Waitlist Manager Agent
- Slot Optimizer Agent
- Upsell Engine Agent
- Dynamic Pricing Agent
- Bundle Creator Agent
- Inventory Intelligence Agent
- Staff Scheduling Agent
- Customer Retention Agent
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json

from app.services.agents import (
    WaitlistManagerAgent,
    SlotOptimizerAgent,
    UpsellEngineAgent,
    DynamicPricingAgent,
    BundleCreatorAgent,
    InventoryIntelligenceAgent,
    StaffSchedulingAgent,
    CustomerRetentionAgent,
    AgentResponse,
    get_agent,
    AGENTS,
)


# ============== Fixtures ==============

@pytest.fixture
def mock_openrouter_client():
    """Mock OpenRouter client"""
    client = AsyncMock()
    response = MagicMock()
    response.content = json.dumps({
        "success": True,
        "message": "Test response",
        "data": {"test": "data"},
        "confidence": 0.9
    })
    client.chat = AsyncMock(return_value=response)
    return client


@pytest.fixture
def mock_cache_service():
    """Mock cache service"""
    cache = AsyncMock()
    cache.get = AsyncMock(return_value=None)
    cache.set = AsyncMock(return_value=True)
    cache._generate_key = MagicMock(return_value="test_key")
    return cache


@pytest.fixture
def sample_cancelled_booking():
    """Sample cancelled booking data"""
    return {
        "id": "booking_123",
        "service_name": "Hair Cut",
        "date": "2024-02-20",
        "time": "10:00",
        "staff_name": "Priya",
        "duration": 45,
        "price": 500
    }


@pytest.fixture
def sample_waitlist_entries():
    """Sample waitlist entries"""
    return [
        {
            "customer_id": "cust_1",
            "customer_name": "Rahul Sharma",
            "loyalty_tier": "Platinum",
            "created_at": "2024-02-19T09:00:00",
            "service_name": "Hair Cut"
        },
        {
            "customer_id": "cust_2",
            "customer_name": "Priya Patel",
            "loyalty_tier": "Gold",
            "created_at": "2024-02-19T10:00:00",
            "service_name": "Hair Cut"
        },
        {
            "customer_id": "cust_3",
            "customer_name": "Amit Kumar",
            "loyalty_tier": "Silver",
            "created_at": "2024-02-19T08:00:00",
            "service_name": "Hair Cut"
        }
    ]


@pytest.fixture
def sample_schedule_data():
    """Sample schedule data for gap detection"""
    return {
        "staff_id": "staff_1",
        "date": "2024-02-20",
        "bookings": [
            {"time": "09:00", "duration": 60, "service": "Hair Spa"},
            {"time": "10:00", "duration": 45, "service": "Hair Cut"},
            {"time": "12:00", "duration": 30, "service": "Beard Trim"},
            {"time": "14:00", "duration": 60, "service": "Facial"},
        ],
        "working_hours": {"start": "09:00", "end": "18:00"}
    }


@pytest.fixture
def sample_services():
    """Sample services for testing"""
    return [
        {"id": "svc_1", "name": "Hair Cut", "price": 500, "duration": 45},
        {"id": "svc_2", "name": "Beard Trim", "price": 200, "duration": 20},
        {"id": "svc_3", "name": "Hair Spa", "price": 800, "duration": 60},
        {"id": "svc_4", "name": "Facial", "price": 1200, "duration": 60},
    ]


@pytest.fixture
def sample_customer_history():
    """Sample customer booking history"""
    return [
        {"date": "2024-01-15", "service": "Hair Cut", "price": 500},
        {"date": "2024-01-01", "service": "Hair Spa", "price": 800},
        {"date": "2023-12-15", "service": "Facial", "price": 1200},
    ]


# ============== Agent Registry Tests ==============

class TestAgentRegistry:
    """Test agent registry and factory"""
    
    def test_all_agents_registered(self):
        """Verify all 12 agents are registered"""
        expected_agents = [
            "booking", "marketing", "analytics", "support",
            "waitlist", "slot_optimizer", "upsell",
            "dynamic_pricing", "bundle_creator", "inventory",
            "scheduling", "retention"
        ]
        for agent_type in expected_agents:
            assert agent_type in AGENTS, f"Agent {agent_type} not in registry"
    
    def test_get_waitlist_agent(self):
        """Test getting waitlist agent"""
        agent = get_agent("waitlist")
        assert isinstance(agent, WaitlistManagerAgent)
        assert agent.name == "waitlist_agent"
    
    def test_get_slot_optimizer_agent(self):
        """Test getting slot optimizer agent"""
        agent = get_agent("slot_optimizer")
        assert isinstance(agent, SlotOptimizerAgent)
        assert agent.name == "slot_optimizer"
    
    def test_get_upsell_agent(self):
        """Test getting upsell agent"""
        agent = get_agent("upsell")
        assert isinstance(agent, UpsellEngineAgent)
        assert agent.name == "upsell_agent"
    
    def test_get_dynamic_pricing_agent(self):
        """Test getting dynamic pricing agent"""
        agent = get_agent("dynamic_pricing")
        assert isinstance(agent, DynamicPricingAgent)
        assert agent.name == "dynamic_pricing"
    
    def test_get_bundle_creator_agent(self):
        """Test getting bundle creator agent"""
        agent = get_agent("bundle_creator")
        assert isinstance(agent, BundleCreatorAgent)
        assert agent.name == "bundle_creator"
    
    def test_get_inventory_agent(self):
        """Test getting inventory agent"""
        agent = get_agent("inventory")
        assert isinstance(agent, InventoryIntelligenceAgent)
        assert agent.name == "inventory"
    
    def test_get_scheduling_agent(self):
        """Test getting scheduling agent"""
        agent = get_agent("scheduling")
        assert isinstance(agent, StaffSchedulingAgent)
        assert agent.name == "scheduling"
    
    def test_get_retention_agent(self):
        """Test getting retention agent"""
        agent = get_agent("retention")
        assert isinstance(agent, CustomerRetentionAgent)
        assert agent.name == "retention"
    
    def test_get_invalid_agent_raises(self):
        """Test that invalid agent type raises error"""
        with pytest.raises(ValueError, match="Unknown agent type"):
            get_agent("invalid_agent")


# ============== Waitlist Agent Tests ==============

class TestWaitlistManagerAgent:
    """Test Waitlist Manager Agent"""
    
    @pytest.mark.asyncio
    async def test_process_cancellation(self, mock_openrouter_client, mock_cache_service, sample_cancelled_booking, sample_waitlist_entries):
        """Test processing a cancellation"""
        agent = WaitlistManagerAgent()
        agent._client = mock_openrouter_client
        agent._cache = mock_cache_service
        
        response = await agent.process_cancellation(
            cancelled_booking=sample_cancelled_booking,
            waitlist_entries=sample_waitlist_entries,
            context={"salon_id": "salon_1"}
        )
        
        assert isinstance(response, AgentResponse)
        assert response.success is True
        mock_openrouter_client.chat.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_prioritize_waitlist(self, mock_openrouter_client, mock_cache_service, sample_waitlist_entries):
        """Test waitlist prioritization"""
        agent = WaitlistManagerAgent()
        agent._client = mock_openrouter_client
        agent._cache = mock_cache_service
        
        response = await agent.prioritize_waitlist(
            service_id="svc_1",
            preferred_date="2024-02-20",
            waitlist_entries=sample_waitlist_entries,
            context={"salon_id": "salon_1"}
        )
        
        assert isinstance(response, AgentResponse)
        assert response.success is True
    
    @pytest.mark.asyncio
    async def test_generate_notification(self, mock_openrouter_client, mock_cache_service):
        """Test notification generation"""
        agent = WaitlistManagerAgent()
        agent._client = mock_openrouter_client
        agent._cache = mock_cache_service
        
        customer_info = {
            "name": "Rahul Sharma",
            "loyalty_tier": "Platinum",
            "preferred_services": ["Hair Cut"]
        }
        slot_details = {
            "service_name": "Hair Cut",
            "date": "2024-02-20",
            "time": "10:00",
            "staff_name": "Priya"
        }
        
        response = await agent.generate_notification(
            customer_info=customer_info,
            slot_details=slot_details,
            response_deadline_minutes=15,
            context={"salon_id": "salon_1"}
        )
        
        assert isinstance(response, AgentResponse)
        assert response.success is True
    
    @pytest.mark.asyncio
    async def test_handle_escalation(self, mock_openrouter_client, mock_cache_service, sample_waitlist_entries):
        """Test escalation handling"""
        agent = WaitlistManagerAgent()
        agent._client = mock_openrouter_client
        agent._cache = mock_cache_service
        
        response = await agent.handle_escalation(
            original_customer=sample_waitlist_entries[0],
            next_candidates=sample_waitlist_entries[1:],
            slot_details={"time": "10:00", "date": "2024-02-20"},
            context={"salon_id": "salon_1"}
        )
        
        assert isinstance(response, AgentResponse)
        assert response.success is True


# ============== Slot Optimizer Agent Tests ==============

class TestSlotOptimizerAgent:
    """Test Slot Optimizer Agent"""
    
    @pytest.mark.asyncio
    async def test_detect_gaps(self, mock_openrouter_client, mock_cache_service, sample_schedule_data):
        """Test gap detection"""
        agent = SlotOptimizerAgent()
        agent._client = mock_openrouter_client
        agent._cache = mock_cache_service
        
        response = await agent.detect_gaps(
            schedule_data=sample_schedule_data,
            staff_id="staff_1",
            date="2024-02-20",
            context={"salon_id": "salon_1"}
        )
        
        assert isinstance(response, AgentResponse)
        assert response.success is True
    
    @pytest.mark.asyncio
    async def test_generate_gap_offer(self, mock_openrouter_client, mock_cache_service, sample_services):
        """Test gap offer generation"""
        agent = SlotOptimizerAgent()
        agent._client = mock_openrouter_client
        agent._cache = mock_cache_service
        
        gap_details = {
            "start_time": "10:45",
            "end_time": "12:00",
            "duration_minutes": 75,
            "staff_name": "Priya"
        }
        target_customers = [
            {"name": "Rahul", "loyalty_tier": "Platinum", "last_visit": "2024-02-15"}
        ]
        
        response = await agent.generate_gap_offer(
            gap_details=gap_details,
            target_customers=target_customers,
            nearby_services=sample_services,
            context={"salon_id": "salon_1"}
        )
        
        assert isinstance(response, AgentResponse)
        assert response.success is True
    
    @pytest.mark.asyncio
    async def test_suggest_service_combo(self, mock_openrouter_client, mock_cache_service, sample_services):
        """Test service combo suggestions"""
        agent = SlotOptimizerAgent()
        agent._client = mock_openrouter_client
        agent._cache = mock_cache_service
        
        response = await agent.suggest_service_combo(
            gap_duration=75,
            available_services=sample_services,
            customer_preferences={"style": "modern"},
            context={"salon_id": "salon_1"}
        )
        
        assert isinstance(response, AgentResponse)
        assert response.success is True


# ============== Upsell Agent Tests ==============

class TestUpsellEngineAgent:
    """Test Upsell Engine Agent"""
    
    @pytest.mark.asyncio
    async def test_analyze_upsell_potential(self, mock_openrouter_client, mock_cache_service, sample_customer_history):
        """Test upsell potential analysis"""
        agent = UpsellEngineAgent()
        agent._client = mock_openrouter_client
        agent._cache = mock_cache_service
        
        current_booking = {
            "services": [{"name": "Hair Cut", "price": 500}],
            "total": 500,
            "date": "2024-02-20",
            "staff_name": "Priya"
        }
        
        response = await agent.analyze_upsell_potential(
            customer_id="cust_1",
            current_booking=current_booking,
            customer_history=sample_customer_history,
            context={"salon_id": "salon_1"}
        )
        
        assert isinstance(response, AgentResponse)
        assert response.success is True
    
    @pytest.mark.asyncio
    async def test_suggest_addons(self, mock_openrouter_client, mock_cache_service, sample_services):
        """Test add-on suggestions"""
        agent = UpsellEngineAgent()
        agent._client = mock_openrouter_client
        agent._cache = mock_cache_service
        
        booked_services = [{"name": "Hair Cut", "price": 500, "duration": 45}]
        available_addons = [
            {"name": "Beard Trim", "price": 200, "duration": 20},
            {"name": "Hair Spa", "price": 800, "duration": 60}
        ]
        
        response = await agent.suggest_addons(
            booked_services=booked_services,
            available_addons=available_addons,
            customer_preferences={"style": "modern"},
            context={"salon_id": "salon_1"}
        )
        
        assert isinstance(response, AgentResponse)
        assert response.success is True


# ============== Dynamic Pricing Agent Tests ==============

class TestDynamicPricingAgent:
    """Test Dynamic Pricing Agent"""
    
    @pytest.mark.asyncio
    async def test_analyze_demand_patterns(self, mock_openrouter_client, mock_cache_service):
        """Test demand pattern analysis"""
        agent = DynamicPricingAgent()
        agent._client = mock_openrouter_client
        agent._cache = mock_cache_service
        
        historical_data = [
            {"date": "2024-02-01", "bookings": 45, "revenue": 25000},
            {"date": "2024-02-02", "bookings": 38, "revenue": 21000},
        ]
        
        response = await agent.analyze_demand_patterns(
            historical_data=historical_data,
            service_category="hair",
            context={"salon_id": "salon_1"}
        )
        
        assert isinstance(response, AgentResponse)
        assert response.success is True
    
    @pytest.mark.asyncio
    async def test_suggest_peak_pricing(self, mock_openrouter_client, mock_cache_service):
        """Test peak pricing suggestions"""
        agent = DynamicPricingAgent()
        agent._client = mock_openrouter_client
        agent._cache = mock_cache_service
        
        peak_periods = [
            {"day": "Saturday", "hours": ["10:00", "11:00", "12:00"]}
        ]
        current_prices = {"Hair Cut": 500, "Facial": 1200}
        
        response = await agent.suggest_peak_pricing(
            peak_periods=peak_periods,
            current_prices=current_prices,
            demand_forecast={"saturday": "high"},
            context={"salon_id": "salon_1"}
        )
        
        assert isinstance(response, AgentResponse)
        assert response.success is True
    
    @pytest.mark.asyncio
    async def test_suggest_offpeak_discounts(self, mock_openrouter_client, mock_cache_service):
        """Test off-peak discount suggestions"""
        agent = DynamicPricingAgent()
        agent._client = mock_openrouter_client
        agent._cache = mock_cache_service
        
        slow_periods = [
            {"day": "Tuesday", "hours": ["14:00", "15:00", "16:00"]}
        ]
        
        response = await agent.suggest_offpeak_discounts(
            slow_periods=slow_periods,
            current_prices={"Hair Cut": 500},
            utilization_data={"tuesday_afternoon": 0.3},
            context={"salon_id": "salon_1"}
        )
        
        assert isinstance(response, AgentResponse)
        assert response.success is True
    
    @pytest.mark.asyncio
    async def test_analyze_competitor_pricing(self, mock_openrouter_client, mock_cache_service):
        """Test competitor pricing analysis"""
        agent = DynamicPricingAgent()
        agent._client = mock_openrouter_client
        agent._cache = mock_cache_service
        
        competitor_data = [
            {"salon": "Competitor A", "service": "Hair Cut", "price": 450},
            {"salon": "Competitor B", "service": "Hair Cut", "price": 550},
        ]
        
        response = await agent.analyze_competitor_pricing(
            competitor_data=competitor_data,
            our_services={"Hair Cut": 500},
            context={"salon_id": "salon_1"}
        )
        
        assert isinstance(response, AgentResponse)
        assert response.success is True
    
    @pytest.mark.asyncio
    async def test_suggest_festival_pricing(self, mock_openrouter_client, mock_cache_service):
        """Test festival pricing suggestions"""
        agent = DynamicPricingAgent()
        agent._client = mock_openrouter_client
        agent._cache = mock_cache_service
        
        response = await agent.suggest_festival_pricing(
            festival="Diwali",
            festival_dates={"start": "2024-11-01", "end": "2024-11-15"},
            historical_festival_data={"2023": {"bookings": 200, "revenue": 150000}},
            context={"salon_id": "salon_1"}
        )
        
        assert isinstance(response, AgentResponse)
        assert response.success is True


# ============== Bundle Creator Agent Tests ==============

class TestBundleCreatorAgent:
    """Test Bundle Creator Agent"""
    
    @pytest.mark.asyncio
    async def test_create_bridal_bundle(self, mock_openrouter_client, mock_cache_service):
        """Test bridal bundle creation"""
        agent = BundleCreatorAgent()
        agent._client = mock_openrouter_client
        agent._cache = mock_cache_service
        
        response = await agent.create_bridal_bundle(
            budget_range={"min": 15000, "max": 25000},
            services_count=5,
            preferences={"style": "traditional", "skin_type": "oily"},
            context={"salon_id": "salon_1"}
        )
        
        assert isinstance(response, AgentResponse)
        assert response.success is True
    
    @pytest.mark.asyncio
    async def test_create_groom_bundle(self, mock_openrouter_client, mock_cache_service):
        """Test groom bundle creation"""
        agent = BundleCreatorAgent()
        agent._client = mock_openrouter_client
        agent._cache = mock_cache_service
        
        response = await agent.create_groom_bundle(
            budget_range={"min": 5000, "max": 10000},
            services_count=3,
            preferences={"style": "modern", "beard": True},
            context={"salon_id": "salon_1"}
        )
        
        assert isinstance(response, AgentResponse)
        assert response.success is True
    
    @pytest.mark.asyncio
    async def test_create_seasonal_bundle(self, mock_openrouter_client, mock_cache_service):
        """Test seasonal bundle creation"""
        agent = BundleCreatorAgent()
        agent._client = mock_openrouter_client
        agent._cache = mock_cache_service
        
        response = await agent.create_seasonal_bundle(
            season="monsoon",
            occasion="hair care",
            target_segment="premium",
            context={"salon_id": "salon_1"}
        )
        
        assert isinstance(response, AgentResponse)
        assert response.success is True
    
    @pytest.mark.asyncio
    async def test_create_wellness_bundle(self, mock_openrouter_client, mock_cache_service):
        """Test wellness bundle creation"""
        agent = BundleCreatorAgent()
        agent._client = mock_openrouter_client
        agent._cache = mock_cache_service
        
        response = await agent.create_wellness_bundle(
            focus_area="stress_relief",
            duration_minutes=180,
            context={"salon_id": "salon_1"}
        )
        
        assert isinstance(response, AgentResponse)
        assert response.success is True
    
    @pytest.mark.asyncio
    async def test_suggest_custom_combo(self, mock_openrouter_client, mock_cache_service, sample_services):
        """Test custom combo suggestions"""
        agent = BundleCreatorAgent()
        agent._client = mock_openrouter_client
        agent._cache = mock_cache_service
        
        response = await agent.suggest_custom_combo(
            booked_services=[sample_services[0]],
            customer_profile={"loyalty_tier": "Gold", "preferences": ["modern"]},
            available_services=sample_services[1:],
            context={"salon_id": "salon_1"}
        )
        
        assert isinstance(response, AgentResponse)
        assert response.success is True


# ============== Inventory Intelligence Agent Tests ==============

class TestInventoryIntelligenceAgent:
    """Test Inventory Intelligence Agent"""
    
    @pytest.mark.asyncio
    async def test_monitor_stock_levels(self, mock_openrouter_client, mock_cache_service):
        """Test stock level monitoring"""
        agent = InventoryIntelligenceAgent()
        agent._client = mock_openrouter_client
        agent._cache = mock_cache_service
        
        inventory_data = [
            {"product": "Shampoo", "stock": 5, "min_threshold": 10},
            {"product": "Conditioner", "stock": 15, "min_threshold": 10},
        ]
        
        response = await agent.monitor_stock_levels(
            inventory_data=inventory_data,
            threshold_config={"critical": 5, "low": 10},
            context={"salon_id": "salon_1"}
        )
        
        assert isinstance(response, AgentResponse)
        assert response.success is True
    
    @pytest.mark.asyncio
    async def test_predict_reorder_needs(self, mock_openrouter_client, mock_cache_service):
        """Test reorder prediction"""
        agent = InventoryIntelligenceAgent()
        agent._client = mock_openrouter_client
        agent._cache = mock_cache_service
        
        usage_history = [
            {"product": "Shampoo", "daily_usage": 2, "days": 30}
        ]
        
        response = await agent.predict_reorder_needs(
            usage_history=usage_history,
            current_stock={"Shampoo": 20},
            lead_times={"Shampoo": 7},
            context={"salon_id": "salon_1"}
        )
        
        assert isinstance(response, AgentResponse)
        assert response.success is True
    
    @pytest.mark.asyncio
    async def test_check_expiry_alerts(self, mock_openrouter_client, mock_cache_service):
        """Test expiry alert checking"""
        agent = InventoryIntelligenceAgent()
        agent._client = mock_openrouter_client
        agent._cache = mock_cache_service
        
        inventory_data = [
            {"product": "Hair Color", "expiry_date": "2024-03-01"},
            {"product": "Keratin", "expiry_date": "2024-06-01"},
        ]
        
        response = await agent.check_expiry_alerts(
            inventory_data=inventory_data,
            days_threshold=30,
            context={"salon_id": "salon_1"}
        )
        
        assert isinstance(response, AgentResponse)
        assert response.success is True
    
    @pytest.mark.asyncio
    async def test_analyze_usage_patterns(self, mock_openrouter_client, mock_cache_service):
        """Test usage pattern analysis"""
        agent = InventoryIntelligenceAgent()
        agent._client = mock_openrouter_client
        agent._cache = mock_cache_service
        
        usage_data = [
            {"product": "Shampoo", "service": "Hair Wash", "quantity": 15},
        ]
        
        response = await agent.analyze_usage_patterns(
            usage_data=usage_data,
            service_data={"Hair Wash": {"count": 50}},
            context={"salon_id": "salon_1"}
        )
        
        assert isinstance(response, AgentResponse)
        assert response.success is True
    
    @pytest.mark.asyncio
    async def test_suggest_order_quantities(self, mock_openrouter_client, mock_cache_service):
        """Test order quantity suggestions"""
        agent = InventoryIntelligenceAgent()
        agent._client = mock_openrouter_client
        agent._cache = mock_cache_service
        
        response = await agent.suggest_order_quantities(
            product_id="prod_1",
            product_name="Shampoo",
            usage_rate=2.5,
            current_stock=10,
            lead_time=7,
            context={"salon_id": "salon_1"}
        )
        
        assert isinstance(response, AgentResponse)
        assert response.success is True


# ============== Staff Scheduling Agent Tests ==============

class TestStaffSchedulingAgent:
    """Test Staff Scheduling Agent"""
    
    @pytest.mark.asyncio
    async def test_create_weekly_schedule(self, mock_openrouter_client, mock_cache_service):
        """Test weekly schedule creation"""
        agent = StaffSchedulingAgent()
        agent._client = mock_openrouter_client
        agent._cache = mock_cache_service
        
        staff_list = [
            {"id": "staff_1", "name": "Priya", "skills": ["hair", "color"]},
            {"id": "staff_2", "name": "Rahul", "skills": ["beard", "hair"]},
        ]
        
        response = await agent.create_weekly_schedule(
            staff_list=staff_list,
            demand_forecast={"monday": "high", "tuesday": "low"},
            constraints={"max_hours": 48},
            context={"salon_id": "salon_1"}
        )
        
        assert isinstance(response, AgentResponse)
        assert response.success is True
    
    @pytest.mark.asyncio
    async def test_optimize_shifts(self, mock_openrouter_client, mock_cache_service):
        """Test shift optimization"""
        agent = StaffSchedulingAgent()
        agent._client = mock_openrouter_client
        agent._cache = mock_cache_service
        
        current_schedule = {
            "staff_1": {"shift": "morning", "hours": 8},
            "staff_2": {"shift": "evening", "hours": 6},
        }
        
        response = await agent.optimize_shifts(
            current_schedule=current_schedule,
            demand_patterns={"morning": 0.8, "evening": 0.6},
            staff_preferences={"staff_1": "morning"},
            context={"salon_id": "salon_1"}
        )
        
        assert isinstance(response, AgentResponse)
        assert response.success is True
    
    @pytest.mark.asyncio
    async def test_match_skills_to_demand(self, mock_openrouter_client, mock_cache_service):
        """Test skill-demand matching"""
        agent = StaffSchedulingAgent()
        agent._client = mock_openrouter_client
        agent._cache = mock_cache_service
        
        service_demand = [
            {"service": "Hair Cut", "demand": 20},
            {"service": "Hair Color", "demand": 10},
        ]
        
        staff_skills = [
            {"staff_id": "staff_1", "skills": ["hair", "color"]},
        ]
        
        response = await agent.match_skills_to_demand(
            service_demand=service_demand,
            staff_skills=staff_skills,
            context={"salon_id": "salon_1"}
        )
        
        assert isinstance(response, AgentResponse)
        assert response.success is True
    
    @pytest.mark.asyncio
    async def test_handle_time_off_request(self, mock_openrouter_client, mock_cache_service):
        """Test time-off request handling"""
        agent = StaffSchedulingAgent()
        agent._client = mock_openrouter_client
        agent._cache = mock_cache_service
        
        response = await agent.handle_time_off_request(
            request={
                "staff_id": "staff_1",
                "date": "2024-02-25",
                "reason": "personal"
            },
            current_schedule={"staff_1": {"shift": "morning"}},
            available_staff=["staff_2", "staff_3"],
            context={"salon_id": "salon_1"}
        )
        
        assert isinstance(response, AgentResponse)
        assert response.success is True
    
    @pytest.mark.asyncio
    async def test_prevent_overtime(self, mock_openrouter_client, mock_cache_service):
        """Test overtime prevention"""
        agent = StaffSchedulingAgent()
        agent._client = mock_openrouter_client
        agent._cache = mock_cache_service
        
        timesheet_data = [
            {"staff_id": "staff_1", "hours_worked": 45, "week": "2024-W08"},
        ]
        
        response = await agent.prevent_overtime(
            timesheet_data=timesheet_data,
            max_hours_per_week=48,
            context={"salon_id": "salon_1"}
        )
        
        assert isinstance(response, AgentResponse)
        assert response.success is True


# ============== Customer Retention Agent Tests ==============

class TestCustomerRetentionAgent:
    """Test Customer Retention Agent"""
    
    @pytest.mark.asyncio
    async def test_identify_at_risk_customers(self, mock_openrouter_client, mock_cache_service):
        """Test at-risk customer identification"""
        agent = CustomerRetentionAgent()
        agent._client = mock_openrouter_client
        agent._cache = mock_cache_service
        
        customer_data = [
            {"id": "cust_1", "last_visit": "2024-01-01", "visits": 5},
            {"id": "cust_2", "last_visit": "2024-02-15", "visits": 10},
        ]
        
        response = await agent.identify_at_risk_customers(
            customer_data=customer_data,
            visit_threshold_days=45,
            context={"salon_id": "salon_1"}
        )
        
        assert isinstance(response, AgentResponse)
        assert response.success is True
    
    @pytest.mark.asyncio
    async def test_create_winback_campaign(self, mock_openrouter_client, mock_cache_service):
        """Test winback campaign creation"""
        agent = CustomerRetentionAgent()
        agent._client = mock_openrouter_client
        agent._cache = mock_cache_service
        
        response = await agent.create_winback_campaign(
            customer_segment="lapsed",
            last_visit_range={"min": 60, "max": 180},
            offer_budget=5000,
            context={"salon_id": "salon_1"}
        )
        
        assert isinstance(response, AgentResponse)
        assert response.success is True
    
    @pytest.mark.asyncio
    async def test_optimize_loyalty_program(self, mock_openrouter_client, mock_cache_service):
        """Test loyalty program optimization"""
        agent = CustomerRetentionAgent()
        agent._client = mock_openrouter_client
        agent._cache = mock_cache_service
        
        loyalty_data = {
            "total_members": 500,
            "active_members": 350,
            "points_redeemed": 50000
        }
        
        response = await agent.optimize_loyalty_program(
            loyalty_data=loyalty_data,
            customer_feedback=["More rewards", "Better tiers"],
            context={"salon_id": "salon_1"}
        )
        
        assert isinstance(response, AgentResponse)
        assert response.success is True
    
    @pytest.mark.asyncio
    async def test_create_reengagement_trigger(self, mock_openrouter_client, mock_cache_service):
        """Test re-engagement trigger creation"""
        agent = CustomerRetentionAgent()
        agent._client = mock_openrouter_client
        agent._cache = mock_cache_service
        
        response = await agent.create_reengagement_trigger(
            customer_profile={
                "id": "cust_1",
                "last_visit": "2024-01-01",
                "favorite_service": "Hair Cut"
            },
            trigger_event="30_days_inactive",
            context={"salon_id": "salon_1"}
        )
        
        assert isinstance(response, AgentResponse)
        assert response.success is True
    
    @pytest.mark.asyncio
    async def test_analyze_churn_factors(self, mock_openrouter_client, mock_cache_service):
        """Test churn factor analysis"""
        agent = CustomerRetentionAgent()
        agent._client = mock_openrouter_client
        agent._cache = mock_cache_service
        
        churned_customers = [
            {"id": "cust_1", "reason": "price", "visits": 3},
        ]
        active_customers = [
            {"id": "cust_2", "visits": 15},
        ]
        
        response = await agent.analyze_churn_factors(
            churned_customers=churned_customers,
            active_customers=active_customers,
            context={"salon_id": "salon_1"}
        )
        
        assert isinstance(response, AgentResponse)
        assert response.success is True


# ============== Integration Tests ==============

class TestAgentIntegration:
    """Integration tests for agent workflows"""
    
    @pytest.mark.asyncio
    async def test_waitlist_workflow(self, mock_openrouter_client, mock_cache_service, sample_cancelled_booking, sample_waitlist_entries):
        """Test complete waitlist workflow"""
        agent = WaitlistManagerAgent()
        agent._client = mock_openrouter_client
        agent._cache = mock_cache_service
        
        # Step 1: Process cancellation
        process_response = await agent.process_cancellation(
            cancelled_booking=sample_cancelled_booking,
            waitlist_entries=sample_waitlist_entries
        )
        assert process_response.success
        
        # Step 2: Generate notification for top candidate
        notification_response = await agent.generate_notification(
            customer_info=sample_waitlist_entries[0],
            slot_details=sample_cancelled_booking
        )
        assert notification_response.success
    
    @pytest.mark.asyncio
    async def test_pricing_bundle_workflow(self, mock_openrouter_client, mock_cache_service):
        """Test pricing + bundle creation workflow"""
        # Step 1: Analyze demand for pricing
        pricing_agent = DynamicPricingAgent()
        pricing_agent._client = mock_openrouter_client
        pricing_agent._cache = mock_cache_service
        
        pricing_response = await pricing_agent.suggest_festival_pricing(
            festival="Diwali",
            festival_dates={"start": "2024-11-01", "end": "2024-11-15"},
            historical_festival_data={}
        )
        assert pricing_response.success
        
        # Step 2: Create festival bundle
        bundle_agent = BundleCreatorAgent()
        bundle_agent._client = mock_openrouter_client
        bundle_agent._cache = mock_cache_service
        
        bundle_response = await bundle_agent.create_seasonal_bundle(
            season="festival",
            occasion="Diwali",
            target_segment="all"
        )
        assert bundle_response.success
    
    @pytest.mark.asyncio
    async def test_inventory_scheduling_workflow(self, mock_openrouter_client, mock_cache_service):
        """Test inventory + scheduling workflow"""
        # Step 1: Check inventory
        inventory_agent = InventoryIntelligenceAgent()
        inventory_agent._client = mock_openrouter_client
        inventory_agent._cache = mock_cache_service
        
        inventory_response = await inventory_agent.monitor_stock_levels(
            inventory_data=[{"product": "Hair Color", "stock": 5}],
            threshold_config={"low": 10}
        )
        assert inventory_response.success
        
        # Step 2: Adjust scheduling based on inventory
        scheduling_agent = StaffSchedulingAgent()
        scheduling_agent._client = mock_openrouter_client
        scheduling_agent._cache = mock_cache_service
        
        schedule_response = await scheduling_agent.optimize_shifts(
            current_schedule={},
            demand_patterns={},
            staff_preferences={}
        )
        assert schedule_response.success
    
    @pytest.mark.asyncio
    async def test_retention_upsell_workflow(self, mock_openrouter_client, mock_cache_service):
        """Test retention + upsell workflow"""
        # Step 1: Identify at-risk customers
        retention_agent = CustomerRetentionAgent()
        retention_agent._client = mock_openrouter_client
        retention_agent._cache = mock_cache_service
        
        retention_response = await retention_agent.create_winback_campaign(
            customer_segment="at_risk",
            last_visit_range={"min": 30, "max": 60},
            offer_budget=3000
        )
        assert retention_response.success
        
        # Step 2: Create upsell for winback
        upsell_agent = UpsellEngineAgent()
        upsell_agent._client = mock_openrouter_client
        upsell_agent._cache = mock_cache_service
        
        upsell_response = await upsell_agent.create_combo_offer(
            base_services=[{"name": "Hair Cut", "price": 500}],
            customer_segment="winback",
            occasion="special_offer"
        )
        assert upsell_response.success


# Run tests with: pytest tests/ai/test_new_agents.py -v
