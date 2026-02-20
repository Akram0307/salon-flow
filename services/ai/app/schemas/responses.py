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
