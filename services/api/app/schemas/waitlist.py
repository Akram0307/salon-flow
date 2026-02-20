"""Waitlist Schemas"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class WaitlistStatus(str, Enum):
    WAITING = "waiting"
    NOTIFIED = "notified"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class WaitlistPriority(str, Enum):
    NORMAL = "normal"
    HIGH = "high"
    VIP = "vip"


class WaitlistEntryBase(BaseModel):
    """Base waitlist entry schema"""
    customer_id: str
    service_id: str
    preferred_staff_id: Optional[str] = None
    preferred_time_start: Optional[datetime] = None
    preferred_time_end: Optional[datetime] = None
    notes: Optional[str] = None
    priority: WaitlistPriority = WaitlistPriority.NORMAL


class WaitlistEntryCreate(WaitlistEntryBase):
    """Schema for creating a waitlist entry"""
    salon_id: Optional[str] = None  # Injected from auth


class WaitlistEntryUpdate(BaseModel):
    """Schema for updating a waitlist entry"""
    preferred_staff_id: Optional[str] = None
    preferred_time_start: Optional[datetime] = None
    preferred_time_end: Optional[datetime] = None
    notes: Optional[str] = None
    priority: Optional[WaitlistPriority] = None
    status: Optional[WaitlistStatus] = None


class WaitlistEntryResponse(WaitlistEntryBase):
    """Schema for waitlist entry response"""
    id: str
    salon_id: str
    queue_position: int
    status: WaitlistStatus
    estimated_wait_minutes: Optional[int] = None
    notified_at: Optional[datetime] = None
    confirmed_at: Optional[datetime] = None
    booking_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WaitlistSummary(BaseModel):
    """Schema for waitlist summary"""
    total_waiting: int
    average_wait_time: int  # minutes
    by_service: dict
    by_priority: dict
    oldest_entry_minutes: int
