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
