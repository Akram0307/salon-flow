"""Feedback and Reviews Schemas"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class FeedbackType(str, Enum):
    REVIEW = "review"
    COMPLAINT = "complaint"
    SUGGESTION = "suggestion"
    COMPLIMENT = "compliment"


class FeedbackStatus(str, Enum):
    PENDING = "pending"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class FeedbackPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class FeedbackBase(BaseModel):
    """Base feedback schema"""
    customer_id: str
    booking_id: Optional[str] = None
    feedback_type: FeedbackType
    rating: Optional[int] = Field(None, ge=1, le=5)
    title: Optional[str] = Field(None, max_length=200)
    comment: Optional[str] = Field(None, max_length=2000)
    staff_id: Optional[str] = None  # Staff member being reviewed
    service_id: Optional[str] = None  # Service being reviewed


class FeedbackCreate(FeedbackBase):
    """Schema for creating feedback"""
    salon_id: Optional[str] = None  # Injected from auth


class FeedbackUpdate(BaseModel):
    """Schema for updating feedback"""
    status: Optional[FeedbackStatus] = None
    priority: Optional[FeedbackPriority] = None
    internal_notes: Optional[str] = None
    resolution_notes: Optional[str] = None


class FeedbackResponse(FeedbackBase):
    """Schema for feedback response"""
    id: str
    salon_id: str
    status: FeedbackStatus
    priority: FeedbackPriority
    internal_notes: Optional[str] = None
    resolution_notes: Optional[str] = None
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FeedbackReplyBase(BaseModel):
    """Base feedback reply schema"""
    reply_text: str = Field(..., min_length=1, max_length=1000)
    is_public: bool = False


class FeedbackReplyCreate(FeedbackReplyBase):
    """Schema for creating a feedback reply"""
    pass


class FeedbackReplyResponse(FeedbackReplyBase):
    """Schema for feedback reply response"""
    id: str
    feedback_id: str
    salon_id: str
    replied_by: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class FeedbackSummary(BaseModel):
    """Schema for feedback summary"""
    total_feedback: int
    average_rating: Optional[Decimal] = None
    rating_distribution: dict
    by_type: dict
    by_status: dict
    pending_complaints: int
    top_rated_staff: List[dict]
    low_rated_services: List[dict]
