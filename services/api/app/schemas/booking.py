"""
Booking schemas for Salon Flow SaaS.
Handles appointment booking lifecycle, status transitions, and resource allocation.
"""
from datetime import datetime, date as date_type, time as time_type
from decimal import Decimal
from typing import Optional, Dict, List, Any
from enum import Enum

from pydantic import Field, field_validator, model_validator, computed_field

from .base import (
    FirestoreModel,
    TimestampMixin,
    BookingStatus,
    BookingChannel,
    BusinessConstants,
    generate_entity_id,
    is_late_arrival,
)


# ============================================================================
# BOOKING TIME SLOT
# ============================================================================

class TimeSlot(FirestoreModel):
    """Represents a bookable time slot."""
    start_time: time_type = Field(..., description="Slot start time")
    end_time: time_type = Field(..., description="Slot end time")
    slot_date: date_type = Field(..., description="Slot date")
    
    @model_validator(mode='after')
    def validate_times(self) -> 'TimeSlot':
        if self.start_time >= self.end_time:
            raise ValueError("Start time must be before end time")
        return self
    
    @property
    def duration_minutes(self) -> int:
        """Calculate slot duration in minutes."""
        start_minutes = self.start_time.hour * 60 + self.start_time.minute
        end_minutes = self.end_time.hour * 60 + self.end_time.minute
        return end_minutes - start_minutes
    
    def overlaps(self, other: 'TimeSlot') -> bool:
        """Check if this slot overlaps with another."""
        if self.slot_date != other.slot_date:
            return False
        return not (self.end_time <= other.start_time or self.start_time >= other.end_time)
    
    def to_firestore(self) -> Dict[str, Any]:
        data = super().to_firestore()
        data['start_time'] = self.start_time.isoformat()
        data['end_time'] = self.end_time.isoformat()
        data['slot_date'] = self.slot_date.isoformat()
        return data


class BookingTimeSlot(FirestoreModel):
    """Time slot with booking-specific details."""
    start_time: time_type = Field(..., description="Booking start time")
    end_time: time_type = Field(..., description="Booking end time")
    booking_date: date_type = Field(..., description="Booking date")
    duration_minutes: int = Field(..., description="Total duration in minutes")
    
    @model_validator(mode='after')
    def validate_times(self) -> 'BookingTimeSlot':
        if self.start_time >= self.end_time:
            raise ValueError("Start time must be before end time")
        return self


class BookingServiceDetails(FirestoreModel):
    """Service details for a booking."""
    service_id: str = Field(..., description="Service ID")
    service_name: str = Field(..., description="Service name")
    base_price: Decimal = Field(..., description="Base price before GST")
    duration_minutes: int = Field(..., description="Service duration")
    category: str = Field(..., description="Service category")
    resource_type: str = Field(default="any", description="Required resource type")
    
    def to_firestore(self) -> Dict[str, Any]:
        data = super().to_firestore()
        data['base_price'] = float(self.base_price)
        return data


class BookingStaffDetails(FirestoreModel):
    """Staff details for a booking."""
    staff_id: str = Field(..., description="Staff ID")
    staff_name: str = Field(..., description="Staff name")
    role: str = Field(default="stylist", description="Staff role")
    expertise_level: str = Field(default="intermediate", description="Expertise level")


class BookingCustomerDetails(FirestoreModel):
    """Customer details for a booking."""
    customer_id: str = Field(..., description="Customer ID")
    customer_name: str = Field(..., description="Customer name")
    customer_phone: str = Field(..., description="Customer phone")
    customer_email: Optional[str] = Field(default=None, description="Customer email")


class BookingResourceDetails(FirestoreModel):
    """Resource details for a booking."""
    resource_id: str = Field(..., description="Resource ID")
    resource_name: str = Field(..., description="Resource name")
    resource_type: str = Field(..., description="Resource type")


# ============================================================================
# BOOKING BASE SCHEMA
# ============================================================================

class BookingBase(FirestoreModel, TimestampMixin):
    """Base booking schema with common fields."""
    salon_id: str = Field(..., description="Salon/Tenant ID")
    
    # Customer info
    customer_id: str = Field(..., description="Customer ID")
    customer_name: str = Field(..., description="Customer name for quick display")
    customer_phone: str = Field(..., description="Customer phone for contact")
    
    # Service info
    service_id: str = Field(..., description="Service ID")
    service_name: str = Field(..., description="Service name for quick display")
    service_price: Decimal = Field(..., description="Service price at booking time")
    service_duration: int = Field(..., description="Service duration in minutes")
    
    # Staff assignment
    staff_id: Optional[str] = Field(default=None, description="Assigned staff ID")
    staff_name: Optional[str] = Field(default=None, description="Assigned staff name")
    
    # Resource assignment
    resource_id: Optional[str] = Field(default=None, description="Assigned resource ID")
    resource_name: Optional[str] = Field(default=None, description="Assigned resource name")
    
    # Time details
    booking_date: date_type = Field(..., description="Booking date")
    start_time: time_type = Field(..., description="Booking start time")
    end_time: time_type = Field(..., description="Booking end time")
    
    # Status
    status: BookingStatus = Field(default=BookingStatus.PENDING, description="Booking status")
    booking_channel: BookingChannel = Field(default=BookingChannel.ONLINE, description="Booking channel")
    
    # QR Code for check-in
    qr_code: Optional[str] = Field(default=None, description="QR code for check-in")
    
    # Tracking
    check_in_time: Optional[time_type] = Field(default=None, description="Check-in time")
    checkout_time: Optional[time_type] = Field(default=None, description="Checkout time")
    actual_duration: Optional[int] = Field(default=None, description="Actual service duration")
    actual_price: Optional[Decimal] = Field(default=None, description="Actual price after upsells")
    
    # Late arrival tracking
    is_late_arrival: bool = Field(default=False, description="Whether customer arrived late")
    late_arrival_minutes: int = Field(default=0, description="Minutes late")
    
    # Notes
    notes: Optional[str] = Field(default=None, description="Customer notes")
    internal_notes: Optional[str] = Field(default=None, description="Internal staff notes")
    
    def to_firestore(self) -> Dict[str, Any]:
        data = super().to_firestore()
        data['service_price'] = float(self.service_price)
        if self.actual_price:
            data['actual_price'] = float(self.actual_price)
        data['booking_date'] = self.booking_date.isoformat()
        data['start_time'] = self.start_time.isoformat()
        data['end_time'] = self.end_time.isoformat()
        if self.check_in_time:
            data['check_in_time'] = self.check_in_time.isoformat()
        if self.checkout_time:
            data['checkout_time'] = self.checkout_time.isoformat()
        return data


class BookingCreate(BookingBase):
    """Schema for creating a new booking."""
    pass


class BookingUpdate(FirestoreModel):
    """Schema for updating an existing booking."""
    staff_id: Optional[str] = Field(default=None)
    staff_name: Optional[str] = Field(default=None)
    resource_id: Optional[str] = Field(default=None)
    resource_name: Optional[str] = Field(default=None)
    start_time: Optional[time_type] = Field(default=None)
    end_time: Optional[time_type] = Field(default=None)
    status: Optional[BookingStatus] = Field(default=None)
    notes: Optional[str] = Field(default=None)
    internal_notes: Optional[str] = Field(default=None)


class BookingStatusUpdate(FirestoreModel):
    """Schema for updating booking status."""
    status: BookingStatus = Field(..., description="New booking status")
    notes: Optional[str] = Field(default=None, description="Optional notes")


class Booking(BookingBase):
    """Complete booking schema with all fields."""
    id: str = Field(default_factory=lambda: generate_entity_id("booking"))
    payment_id: Optional[str] = Field(default=None, description="Associated payment ID")
    upsell_services: List[Dict[str, Any]] = Field(default_factory=list, description="Upsell services added")


class BookingSummary(FirestoreModel):
    """Summary view of a booking for lists."""
    id: str
    salon_id: str
    customer_name: str
    customer_phone: str
    service_name: str
    staff_name: Optional[str]
    booking_date: date_type
    start_time: time_type
    status: BookingStatus
    service_price: Decimal


class BookingCalendarEvent(FirestoreModel):
    """Booking formatted for calendar display."""
    id: str
    title: str
    start: datetime
    end: datetime
    status: BookingStatus
    customer_name: str
    service_name: str
    staff_name: Optional[str]
    color: str = Field(default="blue", description="Event color")


class BookingSearch(FirestoreModel):
    """Search parameters for bookings."""
    salon_id: str
    customer_id: Optional[str] = None
    staff_id: Optional[str] = None
    status: Optional[BookingStatus] = None
    booking_date_from: Optional[date_type] = None
    booking_date_to: Optional[date_type] = None
    booking_channel: Optional[BookingChannel] = None


class BookingStats(FirestoreModel):
    """Booking statistics."""
    total_bookings: int = Field(default=0)
    completed_bookings: int = Field(default=0)
    cancelled_bookings: int = Field(default=0)
    no_show_bookings: int = Field(default=0)
    total_revenue: Decimal = Field(default=Decimal("0"))
    average_service_value: Decimal = Field(default=Decimal("0"))
    
    def to_firestore(self) -> Dict[str, Any]:
        data = super().to_firestore()
        data['total_revenue'] = float(self.total_revenue)
        data['average_service_value'] = float(self.average_service_value)
        return data
