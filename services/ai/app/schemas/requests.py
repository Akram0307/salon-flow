"""Request schemas for AI Service"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Chat request schema"""
    message: str = Field(..., min_length=1, max_length=4000)
    salon_id: str = Field(..., description="Salon ID for context")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")
    agent_type: str = Field(default="booking", description="Agent type: booking, marketing, analytics, support")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")


class BookingSuggestionRequest(BaseModel):
    """Booking suggestion request"""
    salon_id: str
    service_ids: List[str]
    preferred_date: str
    preferred_time: Optional[str] = None
    staff_preference: Optional[str] = None
    customer_id: Optional[str] = None


class StylistRecommendationRequest(BaseModel):
    """Stylist recommendation request"""
    salon_id: str
    service_ids: List[str]
    customer_preferences: Optional[Dict[str, Any]] = None


class CampaignRequest(BaseModel):
    """Marketing campaign request"""
    salon_id: str
    campaign_type: str = Field(..., description="Type: promotional, seasonal, loyalty, birthday")
    target_audience: Dict[str, Any]
    offer_details: Dict[str, Any]


class AnalyticsRequest(BaseModel):
    """Analytics request"""
    salon_id: str
    analysis_type: str = Field(..., description="Type: revenue, staff, demand, trends")
    period: str = Field(..., description="Time period: week, month, quarter, year")
    filters: Optional[Dict[str, Any]] = None


class ComplaintRequest(BaseModel):
    """Customer complaint request"""
    salon_id: str
    customer_id: str
    complaint: str
    booking_id: Optional[str] = None


class FeedbackRequest(BaseModel):
    """Feedback generation request"""
    salon_id: str
    customer_name: str
    service_details: Dict[str, Any]


# ============== Waitlist Agent Schemas ==============

class WaitlistProcessRequest(BaseModel):
    """Request to process a cancellation and find waitlist candidates"""
    salon_id: str
    cancelled_booking: Dict[str, Any] = Field(..., description="Details of the cancelled booking")
    waitlist_entries: List[Dict[str, Any]] = Field(..., description="Current waitlist entries")


class WaitlistPrioritizeRequest(BaseModel):
    """Request to prioritize waitlist for a slot"""
    salon_id: str
    service_id: str
    preferred_date: str
    waitlist_entries: List[Dict[str, Any]]


class WaitlistNotificationRequest(BaseModel):
    """Request to generate waitlist notification"""
    salon_id: str
    customer_info: Dict[str, Any]
    slot_details: Dict[str, Any]
    response_deadline_minutes: int = Field(default=15, description="Minutes to respond")


class WaitlistEscalationRequest(BaseModel):
    """Request to handle waitlist escalation"""
    salon_id: str
    original_customer: Dict[str, Any]
    next_candidates: List[Dict[str, Any]]
    slot_details: Dict[str, Any]


# ============== Slot Optimizer Agent Schemas ==============

class GapDetectionRequest(BaseModel):
    """Request to detect schedule gaps"""
    salon_id: str
    staff_id: str
    date: str
    schedule_data: Dict[str, Any]


class GapOfferRequest(BaseModel):
    """Request to generate offer for a gap"""
    salon_id: str
    gap_details: Dict[str, Any]
    target_customers: List[Dict[str, Any]]
    nearby_services: List[Dict[str, Any]]


class ServiceComboRequest(BaseModel):
    """Request to suggest service combinations"""
    salon_id: str
    gap_duration: int = Field(..., description="Gap duration in minutes")
    available_services: List[Dict[str, Any]]
    customer_preferences: Optional[Dict[str, Any]] = None


class ScheduleOptimizationRequest(BaseModel):
    """Request to optimize multiple staff schedules"""
    salon_id: str
    date: str
    staff_schedules: Dict[str, Any]


# ============== Upsell Agent Schemas ==============

class UpsellAnalysisRequest(BaseModel):
    """Request to analyze upsell potential"""
    salon_id: str
    customer_id: str
    current_booking: Dict[str, Any]
    customer_history: List[Dict[str, Any]]


class AddonSuggestionRequest(BaseModel):
    """Request to suggest add-ons"""
    salon_id: str
    booked_services: List[Dict[str, Any]]
    available_addons: List[Dict[str, Any]]
    customer_preferences: Optional[Dict[str, Any]] = None


class UpgradeRecommendationRequest(BaseModel):
    """Request to recommend service upgrade"""
    salon_id: str
    current_service: Dict[str, Any]
    upgrade_options: List[Dict[str, Any]]
    customer_profile: Dict[str, Any]


class ComboOfferRequest(BaseModel):
    """Request to create combo offer"""
    salon_id: str
    base_services: List[Dict[str, Any]]
    customer_segment: str
    occasion: Optional[str] = None


class UpsellTrackingRequest(BaseModel):
    """Request to track upsell success"""
    salon_id: str
    period: str
    upsell_data: List[Dict[str, Any]]


# ============== Dynamic Pricing Agent Schemas ==============

class DemandAnalysisRequest(BaseModel):
    """Request to analyze demand patterns"""
    salon_id: str
    historical_data: Dict[str, Any]
    service_category: Optional[str] = None


class PeakPricingRequest(BaseModel):
    """Request for peak pricing suggestions"""
    salon_id: str
    peak_periods: List[Dict[str, Any]]
    current_prices: Dict[str, float]
    demand_forecast: Dict[str, Any]


class OffPeakDiscountRequest(BaseModel):
    """Request for off-peak discount suggestions"""
    salon_id: str
    slow_periods: List[Dict[str, Any]]
    current_prices: Dict[str, float]
    utilization_data: Dict[str, Any]


class CompetitorPricingRequest(BaseModel):
    """Request for competitor pricing analysis"""
    salon_id: str
    competitor_data: List[Dict[str, Any]]
    our_services: List[Dict[str, Any]]


class FestivalPricingRequest(BaseModel):
    """Request for festival pricing strategy"""
    salon_id: str
    festival: str
    festival_dates: str
    historical_festival_data: Optional[Dict[str, Any]] = None


# ============== Bundle Creator Agent Schemas ==============

class BridalBundleRequest(BaseModel):
    """Request to create bridal package"""
    salon_id: str
    budget_range: Dict[str, float]
    services_count: int = 5
    preferences: Optional[Dict[str, Any]] = None


class GroomBundleRequest(BaseModel):
    """Request to create groom package"""
    salon_id: str
    budget_range: Dict[str, float]
    services_count: int = 3
    preferences: Optional[Dict[str, Any]] = None


class SeasonalBundleRequest(BaseModel):
    """Request to create seasonal package"""
    salon_id: str
    season: str
    occasion: Optional[str] = None
    target_segment: str = "general"


class WellnessBundleRequest(BaseModel):
    """Request to create wellness package"""
    salon_id: str
    focus_area: str
    duration_minutes: int = 120


class CustomComboRequest(BaseModel):
    """Request to suggest custom combo"""
    salon_id: str
    booked_services: List[str]
    customer_profile: Dict[str, Any]
    available_services: List[Dict[str, Any]]


# ============== Inventory Agent Schemas ==============

class StockMonitorRequest(BaseModel):
    """Request to monitor stock levels"""
    salon_id: str
    inventory_data: List[Dict[str, Any]]
    threshold_config: Dict[str, int]


class ReorderPredictionRequest(BaseModel):
    """Request to predict reorder needs"""
    salon_id: str
    usage_history: List[Dict[str, Any]]
    current_stock: Dict[str, Any]
    lead_times: Dict[str, int]


class ExpiryAlertRequest(BaseModel):
    """Request to check expiry alerts"""
    salon_id: str
    inventory_data: List[Dict[str, Any]]
    days_threshold: int = 30


class UsageAnalysisRequest(BaseModel):
    """Request to analyze usage patterns"""
    salon_id: str
    usage_data: List[Dict[str, Any]]
    service_data: List[Dict[str, Any]]


class OrderQuantityRequest(BaseModel):
    """Request to suggest order quantity"""
    salon_id: str
    product_id: str
    product_name: str
    usage_rate: float
    current_stock: int
    lead_time: int


# ============== Staff Scheduling Agent Schemas ==============

class WeeklyScheduleRequest(BaseModel):
    """Request to create weekly schedule"""
    salon_id: str
    staff_list: List[Dict[str, Any]]
    demand_forecast: Dict[str, Any]
    constraints: Dict[str, Any]


class ShiftOptimizationRequest(BaseModel):
    """Request to optimize shifts"""
    salon_id: str
    current_schedule: Dict[str, Any]
    demand_patterns: Dict[str, Any]
    staff_preferences: List[Dict[str, Any]]


class SkillMatchRequest(BaseModel):
    """Request to match skills to demand"""
    salon_id: str
    service_demand: List[Dict[str, Any]]
    staff_skills: List[Dict[str, Any]]


class TimeOffRequest(BaseModel):
    """Request to handle time-off"""
    salon_id: str
    request: Dict[str, Any]
    current_schedule: Dict[str, Any]
    available_staff: List[Dict[str, Any]]


class OvertimePreventionRequest(BaseModel):
    """Request to prevent overtime"""
    salon_id: str
    timesheet_data: List[Dict[str, Any]]
    max_hours_per_week: int = 48


# ============== Customer Retention Agent Schemas ==============

class AtRiskCustomersRequest(BaseModel):
    """Request to identify at-risk customers"""
    salon_id: str
    customer_data: List[Dict[str, Any]]
    visit_threshold_days: int = 45


class WinbackCampaignRequest(BaseModel):
    """Request to create win-back campaign"""
    salon_id: str
    customer_segment: str
    last_visit_range: str
    offer_budget: float


class LoyaltyOptimizationRequest(BaseModel):
    """Request to optimize loyalty program"""
    salon_id: str
    loyalty_data: Dict[str, Any]
    customer_feedback: List[Dict[str, Any]]


class ReengagementTriggerRequest(BaseModel):
    """Request to create re-engagement trigger"""
    salon_id: str
    customer_profile: Dict[str, Any]
    trigger_event: str


class ChurnAnalysisRequest(BaseModel):
    """Request to analyze churn factors"""
    salon_id: str
    churned_customers: List[Dict[str, Any]]
    active_customers: List[Dict[str, Any]]
