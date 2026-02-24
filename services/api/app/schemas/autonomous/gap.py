"""Gap schemas for autonomous agent API."""
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from enum import Enum

from pydantic import BaseModel, Field


class GapStatus(str, Enum):
    OPEN = "open"
    FILLED = "filled"
    EXPIRED = "expired"
    IGNORED = "ignored"


class GapPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class GapCreate(BaseModel):
    """Schema for creating a gap."""
    staff_id: str
    staff_name: str
    date: date
    start_time: datetime
    end_time: datetime
    duration_minutes: int = Field(..., ge=15)
    potential_revenue: float = Field(..., ge=0)
    services_fittable: List[str] = Field(default_factory=list)


class FilledByInfo(BaseModel):
    """Information about who filled a gap."""
    booking_id: str
    customer_id: str
    filled_at: datetime


class GapResponse(BaseModel):
    """Schema for gap response."""
    id: str
    salon_id: str
    staff_id: str
    staff_name: str
    date: date
    start_time: datetime
    end_time: datetime
    duration_minutes: int
    priority: GapPriority
    status: GapStatus
    potential_revenue: float
    services_fittable: List[str]
    fill_attempts: int
    last_attempt_at: Optional[datetime] = None
    filled_by: Optional[FilledByInfo] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GapListResponse(BaseModel):
    """Schema for gap list response."""
    items: List[GapResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


class GapStatsResponse(BaseModel):
    """Schema for gap statistics."""
    date: str
    total_gaps: int
    by_status: Dict[str, int]
    by_priority: Dict[str, int]
    total_duration_minutes: int
    total_potential_revenue: float
    filled_revenue: float
    fill_rate: float
