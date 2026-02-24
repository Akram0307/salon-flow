"""Outreach schemas for autonomous agent API."""
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum

from pydantic import BaseModel, Field


class OutreachChannel(str, Enum):
    WHATSAPP = "whatsapp"
    SMS = "sms"
    PUSH = "push"
    EMAIL = "email"


class OutreachStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    RESPONDED = "responded"
    FAILED = "failed"
    EXPIRED = "expired"


class OutreachType(str, Enum):
    GAP_FILL = "gap_fill"
    NO_SHOW_PREVENTION = "no_show_prevention"
    WAITLIST_PROMOTION = "waitlist_promotion"
    DISCOUNT_OFFER = "discount_offer"
    RETENTION = "retention"
    REBOOKING = "rebooking"


class OutreachCreate(BaseModel):
    """Schema for creating outreach."""
    customer_id: str
    customer_name: str
    customer_phone: str
    outreach_type: OutreachType
    channel: OutreachChannel
    message: str = Field(..., min_length=10, max_length=1000)
    trigger_id: Optional[str] = None
    trigger_type: Optional[str] = None
    offer_details: Optional[Dict[str, Any]] = None
    expires_in_minutes: int = Field(default=15, ge=5, le=60)


class ResponseInfo(BaseModel):
    """Customer response information."""
    received: bool = False
    action: Optional[str] = None
    responded_at: Optional[datetime] = None
    booking_id: Optional[str] = None


class DeliveryInfo(BaseModel):
    """Delivery status information."""
    message_id: Optional[str] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    error: Optional[str] = None


class OutreachResponse(BaseModel):
    """Schema for outreach response."""
    id: str
    salon_id: str
    customer_id: str
    customer_name: str
    customer_phone: str
    outreach_type: OutreachType
    channel: OutreachChannel
    status: OutreachStatus
    message: str
    trigger_id: Optional[str] = None
    trigger_type: Optional[str] = None
    offer_details: Dict[str, Any]
    expires_at: datetime
    attempts: int
    last_attempt_at: Optional[datetime] = None
    response: ResponseInfo
    delivery: DeliveryInfo
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OutreachUpdate(BaseModel):
    """Schema for updating outreach status."""
    status: OutreachStatus
    message_id: Optional[str] = None
    error: Optional[str] = None


class OutreachListResponse(BaseModel):
    """Schema for outreach list response."""
    items: List[OutreachResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


class OutreachStatsResponse(BaseModel):
    """Schema for outreach statistics."""
    total: int
    by_status: Dict[str, int]
    by_channel: Dict[str, int]
    by_type: Dict[str, int]
    conversion_rate: float
    response_rate: float
    avg_response_time_seconds: float
