"""Decision schemas for autonomous agent API."""
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum

from pydantic import BaseModel, Field


class DecisionType(str, Enum):
    GAP_FILL = "gap_fill"
    NO_SHOW_PREVENTION = "no_show_prevention"
    WAITLIST_PROMOTION = "waitlist_promotion"
    DISCOUNT_OFFER = "discount_offer"
    DYNAMIC_PRICING = "dynamic_pricing"


class AutonomyLevel(str, Enum):
    FULL_AUTO = "full_auto"
    SUPERVISED = "supervised"
    MANUAL_ONLY = "manual_only"


class DecisionStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    EXPIRED = "expired"
    REJECTED = "rejected"


class RevenueImpact(BaseModel):
    """Revenue impact of a decision."""
    potential: float = Field(default=0, ge=0)
    actual: float = Field(default=0, ge=0)
    currency: str = Field(default="INR")


class DecisionContext(BaseModel):
    """Context for a decision."""
    trigger_id: Optional[str] = None
    trigger_type: Optional[str] = None
    customer_id: Optional[str] = None
    customer_name: Optional[str] = None
    staff_id: Optional[str] = None
    staff_name: Optional[str] = None
    service_id: Optional[str] = None
    service_name: Optional[str] = None
    time_slot: Optional[str] = None
    additional_data: Dict[str, Any] = Field(default_factory=dict)


class ApprovalInfo(BaseModel):
    """Approval information for a decision."""
    required: bool = False
    status: str = "not_required"
    approval_id: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None


class OutcomeInfo(BaseModel):
    """Outcome of a decision."""
    status: DecisionStatus = DecisionStatus.PENDING
    result: Optional[str] = None
    completed_at: Optional[datetime] = None
    booking_created_id: Optional[str] = None


class DecisionCreate(BaseModel):
    """Schema for creating a decision."""
    agent_name: str = Field(..., min_length=1, max_length=100)
    decision_type: DecisionType
    autonomy_level: AutonomyLevel
    context: DecisionContext
    action_taken: str = Field(..., min_length=1)
    action_details: Dict[str, Any] = Field(default_factory=dict)
    revenue_impact: RevenueImpact = Field(default_factory=RevenueImpact)
    approval_required: bool = False


class DecisionResponse(BaseModel):
    """Schema for decision response."""
    id: str
    salon_id: str
    agent_name: str
    decision_type: DecisionType
    autonomy_level: AutonomyLevel
    context: DecisionContext
    action_taken: str
    action_details: Dict[str, Any]
    revenue_impact: RevenueImpact
    approval: ApprovalInfo
    outcome: OutcomeInfo
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DecisionUpdate(BaseModel):
    """Schema for updating a decision."""
    outcome_status: Optional[DecisionStatus] = None
    outcome_result: Optional[str] = None
    booking_created_id: Optional[str] = None


class DecisionListResponse(BaseModel):
    """Schema for decision list response."""
    items: List[DecisionResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


class DecisionStatsResponse(BaseModel):
    """Schema for decision statistics."""
    date: str
    total: int
    by_type: Dict[str, int]
    by_status: Dict[str, int]
    revenue: Dict[str, float]
    success_rate: Optional[float] = None
