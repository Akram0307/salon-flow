"""
Resource schemas for Salon Flow SaaS.
Handles salon layout, chairs, rooms, and resource allocation.
"""
from datetime import datetime, date as date_type, time as time_type
from decimal import Decimal
from typing import Optional, Dict, List, Any

from pydantic import Field, field_validator, model_validator

from .base import (
    FirestoreModel,
    TimestampMixin,
    ResourceType,
    generate_entity_id,
)


# ============================================================================
# RESOURCE CONFIGURATION
# ============================================================================

class ResourceCapacity(FirestoreModel):
    """Resource capacity configuration."""
    max_concurrent_services: int = Field(default=1, ge=1, description="Max services at once")
    avg_service_duration_minutes: int = Field(default=30, ge=5, description="Average service duration")
    max_daily_bookings: int = Field(default=20, ge=1, description="Max bookings per day")
    
    @property
    def hourly_capacity(self) -> float:
        """Calculate hourly service capacity."""
        return (60 / self.avg_service_duration_minutes) * self.max_concurrent_services


class ResourceAvailabilitySlot(FirestoreModel):
    """Resource availability for a specific time."""
    slot_date: date_type = Field(..., description="Date")
    start_time: time_type = Field(..., description="Available from")
    end_time: time_type = Field(..., description="Available until")
    is_available: bool = Field(default=True, description="Is available")
    blocked_reason: Optional[str] = Field(default=None, description="Reason if blocked")
    
    @model_validator(mode='after')
    def validate_times(self) -> 'ResourceAvailabilitySlot':
        if self.start_time >= self.end_time:
            raise ValueError("Start time must be before end time")
        return self
    
    def to_firestore(self) -> Dict[str, Any]:
        data = super().to_firestore()
        data['slot_date'] = self.slot_date.isoformat()
        data['start_time'] = self.start_time.isoformat()
        data['end_time'] = self.end_time.isoformat()
        return data


class ResourceMaintenance(FirestoreModel):
    """Resource maintenance schedule."""
    maintenance_id: str = Field(default_factory=lambda: generate_entity_id("maint"))
    scheduled_date: date_type = Field(..., description="Maintenance date")
    start_time: time_type = Field(..., description="Start time")
    end_time: time_type = Field(..., description="End time")
    reason: str = Field(..., description="Maintenance reason")
    is_completed: bool = Field(default=False)
    notes: Optional[str] = Field(default=None)
    
    def to_firestore(self) -> Dict[str, Any]:
        data = super().to_firestore()
        data['scheduled_date'] = self.scheduled_date.isoformat()
        data['start_time'] = self.start_time.isoformat()
        data['end_time'] = self.end_time.isoformat()
        return data


# ============================================================================
# RESOURCE BASE SCHEMA
# ============================================================================

class ResourceBase(FirestoreModel, TimestampMixin):
    """Base resource schema."""
    salon_id: str = Field(default="", description="Salon ID")
    name: str = Field(..., min_length=1, max_length=50, description="Resource name")
    resource_type: ResourceType = Field(..., description="Resource type")
    zone: Optional[str] = Field(default=None, description="Zone/area in salon")
    capacity: ResourceCapacity = Field(default_factory=ResourceCapacity)
    is_active: bool = Field(default=True)
    is_exclusive: bool = Field(default=False, description="Can only handle one booking at a time")
    blocked_dates: List[str] = Field(default_factory=list, description="Blocked dates (ISO format)")


class ResourceCreate(ResourceBase):
    """Schema for creating a new resource."""
    pass


class ResourceUpdate(FirestoreModel):
    """Schema for updating a resource."""
    name: Optional[str] = Field(default=None, min_length=1, max_length=50)
    zone: Optional[str] = None
    capacity: Optional[ResourceCapacity] = None
    is_active: Optional[bool] = None
    is_exclusive: Optional[bool] = None


class Resource(ResourceBase):
    """Complete resource schema."""
    id: str = Field(default_factory=lambda: generate_entity_id("resource"))
    
    def is_available_at(self, check_date: date_type, check_time: time_type) -> bool:
        """Check if resource is available at given date/time."""
        if not self.is_active:
            return False
        if check_date.isoformat() in self.blocked_dates:
            return False
        return True
    
    def block_date(self, block_date: date_type, reason: str) -> None:
        """Block a specific date."""
        date_str = block_date.isoformat()
        if date_str not in self.blocked_dates:
            self.blocked_dates.append(date_str)
    
    def unblock_date(self, unblock_date: date_type) -> None:
        """Unblock a specific date."""
        date_str = unblock_date.isoformat()
        if date_str in self.blocked_dates:
            self.blocked_dates.remove(date_str)


class ResourceSummary(FirestoreModel):
    """Summary view of a resource."""
    id: str
    salon_id: str
    name: str
    resource_type: ResourceType
    is_active: bool


# ============================================================================
# SALON LAYOUT
# ============================================================================

class SalonLayoutZone(FirestoreModel):
    """Zone within salon layout."""
    name: str = Field(..., description="Zone name")
    zone_type: str = Field(..., description="Zone type (mens, womens, rooms)")
    resources: List[str] = Field(default_factory=list, description="Resource IDs in zone")


class SalonLayoutConfig(FirestoreModel):
    """Complete salon layout configuration."""
    salon_id: str = Field(default="", description="Salon ID")
    zones: List[SalonLayoutZone] = Field(default_factory=list)
    total_mens_chairs: int = Field(default=6)
    total_womens_chairs: int = Field(default=4)
    total_service_rooms: int = Field(default=4)
    total_spa_rooms: int = Field(default=1)
    has_bridal_room: bool = Field(default=True)


class ResourceAllocation(FirestoreModel):
    """Resource allocation for a booking."""
    resource_id: str = Field(..., description="Resource ID")
    booking_id: str = Field(..., description="Booking ID")
    allocation_date: date_type = Field(..., description="Allocation date")
    start_time: time_type = Field(..., description="Start time")
    end_time: time_type = Field(..., description="End time")
    status: str = Field(default="reserved", description="Allocation status")
    
    def to_firestore(self) -> Dict[str, Any]:
        data = super().to_firestore()
        data['allocation_date'] = self.allocation_date.isoformat()
        data['start_time'] = self.start_time.isoformat()
        data['end_time'] = self.end_time.isoformat()
        return data


class ResourceUtilizationReport(FirestoreModel):
    """Resource utilization report."""
    resource_id: str
    resource_name: str
    report_date: date_type
    total_bookings: int = Field(default=0)
    total_minutes_used: int = Field(default=0)
    total_available_minutes: int = Field(default=480)
    utilization_percentage: Decimal = Field(default=Decimal("0"))
    peak_hours: List[str] = Field(default_factory=list)
    
    def to_firestore(self) -> Dict[str, Any]:
        data = super().to_firestore()
        data['report_date'] = self.report_date.isoformat()
        data['utilization_percentage'] = float(self.utilization_percentage)
        return data
