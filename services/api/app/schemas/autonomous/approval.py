"""Approval schemas for autonomous agent API."""
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum

from pydantic import BaseModel, Field


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class ApprovalPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class ApprovalRequestCreate(BaseModel):
    """Schema for creating an approval request."""
    decision_id: str
    agent_name: str
    action_type: str
    action_summary: str = Field(..., min_length=10, max_length=500)
    action_details: Dict[str, Any]
    priority: ApprovalPriority = ApprovalPriority.MEDIUM
    expires_in_minutes: Optional[int] = Field(None, ge=1, le=60)


class ApprovalResponse(BaseModel):
    """Response information for approval."""
    action: Optional[str] = None
    responded_by: Optional[str] = None
    responded_at: Optional[datetime] = None
    notes: Optional[str] = None


class NotificationsSent(BaseModel):
    """Track which notifications were sent."""
    whatsapp: bool = False
    push: bool = False
    email: bool = False


class ApprovalRequestResponse(BaseModel):
    """Schema for approval request response."""
    id: str
    salon_id: str
    decision_id: str
    agent_name: str
    action_type: str
    action_summary: str
    action_details: Dict[str, Any]
    priority: ApprovalPriority
    status: ApprovalStatus
    expires_at: datetime
    notifications_sent: NotificationsSent
    response: ApprovalResponse
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ApprovalAction(BaseModel):
    """Schema for approval action (approve/reject)."""
    action: str = Field(..., pattern="^(approve|reject)$")
    notes: Optional[str] = None


class ApprovalListResponse(BaseModel):
    """Schema for approval list response."""
    items: List[ApprovalRequestResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


class ApprovalStatsResponse(BaseModel):
    """Schema for approval statistics."""
    total: int
    by_status: Dict[str, int]
    by_priority: Dict[str, int]
    avg_response_time_seconds: float
    approval_rate: float
