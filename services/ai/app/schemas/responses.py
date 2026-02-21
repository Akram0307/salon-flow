"""Response schemas for AI Service"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class AIResponse(BaseModel):
    """Standard AI response"""
    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None
    suggestions: Optional[List[str]] = None
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    cached: bool = False
    model_used: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatResponse(BaseModel):
    """Chat response with session info"""
    response: str
    session_id: str
    agent_type: str
    suggestions: Optional[List[str]] = None
    actions: Optional[List[Dict[str, Any]]] = None


class BookingSuggestionResponse(BaseModel):
    """Booking suggestion response"""
    time_slots: List[Dict[str, Any]]
    recommended_stylist: Optional[Dict[str, Any]] = None
    reasoning: str
    alternatives: Optional[List[Dict[str, Any]]] = None


class CampaignResponse(BaseModel):
    """Marketing campaign response"""
    headline: str
    message: str
    call_to_action: str
    best_send_time: str
    engagement_tips: List[str]
    channels: List[str]


class AnalyticsResponse(BaseModel):
    """Analytics response"""
    summary: str
    metrics: Dict[str, Any]
    trends: List[Dict[str, Any]]
    recommendations: List[str]
    charts_data: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    version: str
    openrouter_connected: bool
    redis_connected: bool
    models_available: List[str]


class WaitlistCandidateResponse(BaseModel):
    """Waitlist candidate with priority"""
    customer_id: str
    customer_name: str
    loyalty_tier: str
    priority_score: float
    notification_message: str
    escalation_order: int


class WaitlistProcessResponse(BaseModel):
    """Response for waitlist processing"""
    cancelled_booking_id: str
    top_candidates: List[WaitlistCandidateResponse]
    notification_sequence: List[Dict[str, Any]]
    escalation_timeline: Dict[str, Any]
    fill_probability: float


class GapDetectionResponse(BaseModel):
    """Response for gap detection"""
    staff_id: str
    date: str
    gaps: List[Dict[str, Any]]
    total_gap_minutes: int
    potential_revenue_loss: float
    priority_actions: List[Dict[str, Any]]


class GapOfferResponse(BaseModel):
    """Response for gap offer generation"""
    gap_id: str
    filling_strategy: str
    target_customers: List[Dict[str, Any]]
    offer_messages: List[Dict[str, str]]
    discount_recommendation: Optional[float]
    service_combinations: List[Dict[str, Any]]
    fill_probability: float


class ServiceComboResponse(BaseModel):
    """Response for service combo suggestions"""
    combinations: List[Dict[str, Any]]
    revenue_potential: List[float]
    customer_appeal_scores: List[float]
    recommended_pricing: List[Dict[str, float]]


class UpsellAnalysisResponse(BaseModel):
    """Response for upsell analysis"""
    customer_id: str
    upsell_potential_score: float
    opportunities: List[Dict[str, Any]]
    recommended_approach: str
    expected_value_increase: float
    risk_assessment: str


class AddonSuggestionResponse(BaseModel):
    """Response for add-on suggestions"""
    suggestions: List[Dict[str, Any]]
    compatibility_scores: List[float]
    suggested_pricing: List[Dict[str, float]]
    presentation_messages: List[str]
    expected_acceptance_rates: List[float]


class UpgradeRecommendationResponse(BaseModel):
    """Response for upgrade recommendation"""
    recommended_upgrade: Dict[str, Any]
    value_proposition: str
    price_difference: float
    personalized_message: str
    success_probability: float


class ComboOfferResponse(BaseModel):
    """Response for combo offer creation"""
    combo_name: str
    combo_description: str
    included_services: List[Dict[str, Any]]
    individual_total: float
    combo_price: float
    discount_percentage: float
    value_proposition: str
    validity_period: str
    target_profile: str
    expected_conversion_rate: float


class UpsellTrackingResponse(BaseModel):
    """Response for upsell tracking analysis"""
    period: str
    overall_success_rate: float
    success_by_type: Dict[str, float]
    revenue_impact: Dict[str, float]
    top_performers: List[Dict[str, Any]]
    underperformers: List[Dict[str, Any]]
    recommendations: List[str]
    ab_test_suggestions: List[Dict[str, Any]]
