"""
Shift schemas for Salon Flow SaaS.
Handles staff scheduling, shifts, and leave management.
"""
from datetime import datetime, date as date_type, time as time_type
from decimal import Decimal
from typing import Optional, Dict, List, Any
from enum import Enum

from pydantic import Field, field_validator, model_validator

from .base import (
    FirestoreModel,
    TimestampMixin,
    StaffRole,
    generate_entity_id,
)


class ShiftType(str, Enum):
    """Shift type enumeration."""
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"
    FULL_DAY = "full_day"


class LeaveType(str, Enum):
    """Leave type enumeration."""
    SICK = "sick"
    CASUAL = "casual"
    EARNED = "earned"
    UNPAID = "unpaid"


class LeaveStatus(str, Enum):
    """Leave request status."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class ShiftStatus(str, Enum):
    """Shift status enumeration."""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ShiftTemplate(FirestoreModel):
    """Template for recurring shifts."""
    name: str = Field(..., description="Template name")
    start_time: time_type = Field(..., description="Shift start time")
    end_time: time_type = Field(..., description="Shift end time")
    break_minutes: int = Field(default=30, description="Break duration in minutes")
    
    @model_validator(mode='after')
    def validate_times(self) -> 'ShiftTemplate':
        if self.start_time >= self.end_time:
            raise ValueError("Start time must be before end time")
        return self


class ShiftBase(FirestoreModel, TimestampMixin):
    """Base shift schema."""
    salon_id: str = Field(default="", description="Salon ID")
    staff_id: str = Field(..., description="Staff ID")
    shift_date: date_type = Field(..., description="Shift date")
    start_time: time_type = Field(..., description="Shift start time")
    end_time: time_type = Field(..., description="Shift end time")
    shift_type: ShiftType = Field(default=ShiftType.FULL_DAY)
    status: ShiftStatus = Field(default=ShiftStatus.SCHEDULED)
    is_off_day: bool = Field(default=False)
    notes: Optional[str] = Field(default=None)
    
    @model_validator(mode='after')
    def validate_times(self) -> 'ShiftBase':
        if not self.is_off_day and self.start_time >= self.end_time:
            raise ValueError("Start time must be before end time")
        return self
    
    def to_firestore(self) -> Dict[str, Any]:
        data = super().to_firestore()
        data['shift_date'] = self.shift_date.isoformat()
        data['start_time'] = self.start_time.isoformat()
        data['end_time'] = self.end_time.isoformat()
        return data


class ShiftCreate(ShiftBase):
    """Schema for creating a new shift."""
    pass


class ShiftUpdate(FirestoreModel):
    """Schema for updating a shift."""
    start_time: Optional[time_type] = None
    end_time: Optional[time_type] = None
    shift_type: Optional[ShiftType] = None
    status: Optional[ShiftStatus] = None
    is_off_day: Optional[bool] = None
    notes: Optional[str] = None


class Shift(ShiftBase):
    """Complete shift schema."""
    id: str = Field(default_factory=lambda: generate_entity_id("shift"))


class ShiftSummary(FirestoreModel):
    """Summary view of a shift."""
    id: str
    staff_id: str
    shift_date: date_type
    start_time: time_type
    end_time: time_type
    status: ShiftStatus


class LeaveBalance(FirestoreModel):
    """Staff leave balance."""
    staff_id: str
    year: int
    sick_leave_total: int = Field(default=5)
    sick_leave_used: int = Field(default=0)
    casual_leave_total: int = Field(default=10)
    casual_leave_used: int = Field(default=0)
    earned_leave_total: int = Field(default=15)
    earned_leave_used: int = Field(default=0)
    
    @property
    def sick_leave_remaining(self) -> int:
        return self.sick_leave_total - self.sick_leave_used
    
    @property
    def casual_leave_remaining(self) -> int:
        return self.casual_leave_total - self.casual_leave_used
    
    @property
    def total_remaining(self) -> int:
        return self.sick_leave_remaining + self.casual_leave_remaining + (self.earned_leave_total - self.earned_leave_used)


class LeaveRequest(FirestoreModel, TimestampMixin):
    """Leave request schema."""
    id: str = Field(default_factory=lambda: generate_entity_id("leave"))
    salon_id: str = Field(default="", description="Salon ID")
    staff_id: str = Field(..., description="Staff ID")
    leave_type: LeaveType = Field(..., description="Type of leave")
    start_date: date_type = Field(..., description="Leave start date")
    end_date: date_type = Field(..., description="Leave end date")
    reason: str = Field(..., description="Reason for leave")
    status: LeaveStatus = Field(default=LeaveStatus.PENDING)
    approved_by: Optional[str] = Field(default=None, description="Manager who approved")
    approved_at: Optional[datetime] = Field(default=None)
    rejection_reason: Optional[str] = Field(default=None)
    
    @property
    def duration_days(self) -> int:
        return (self.end_date - self.start_date).days + 1
    
    def to_firestore(self) -> Dict[str, Any]:
        data = super().to_firestore()
        data['start_date'] = self.start_date.isoformat()
        data['end_date'] = self.end_date.isoformat()
        return data


class StaffWeeklySchedule(FirestoreModel):
    """Staff schedule for a week."""
    staff_id: str
    week_start_date: date_type = Field(..., description="Week start date (Monday)")
    week_end_date: date_type = Field(..., description="Week end date (Sunday)")
    shifts: List[Shift] = Field(default_factory=list)
    total_working_hours: int = Field(default=0)
    off_days: List[str] = Field(default_factory=list, description="Off day dates")
    
    def to_firestore(self) -> Dict[str, Any]:
        data = super().to_firestore()
        data['week_start_date'] = self.week_start_date.isoformat()
        data['week_end_date'] = self.week_end_date.isoformat()
        return data


class ScheduleSummary(FirestoreModel):
    """Summary of staff schedules."""
    salon_id: str
    week_start_date: date_type
    week_end_date: date_type
    total_staff: int
    total_shifts: int
    total_off_days: int
    pending_leave_requests: int


class LeaveRequestCreate(FirestoreModel):
    """Schema for creating a leave request."""
    salon_id: str = Field(default="", description="Salon ID")
    staff_id: str = Field(..., description="Staff ID")
    leave_type: LeaveType = Field(..., description="Type of leave")
    start_date: date_type = Field(..., description="Leave start date")
    end_date: date_type = Field(..., description="Leave end date")
    reason: str = Field(..., description="Reason for leave")
    
    def to_firestore(self) -> Dict[str, Any]:
        data = super().to_firestore()
        data['start_date'] = self.start_date.isoformat()
        data['end_date'] = self.end_date.isoformat()
        return data


class LeaveRequestUpdate(FirestoreModel):
    """Schema for updating a leave request."""
    leave_type: Optional[LeaveType] = None
    start_date: Optional[date_type] = None
    end_date: Optional[date_type] = None
    reason: Optional[str] = None
    status: Optional[LeaveStatus] = None

# Alias for backward compatibility
LeaveRequestStatus = LeaveStatus
