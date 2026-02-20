"""
Salon schemas for Salon Flow SaaS.
Handles multi-tenant salon configuration, settings, and layout.
"""
from datetime import datetime, date as date_type, time as time_type
from decimal import Decimal
from typing import Optional, Dict, List, Any

from pydantic import Field, field_validator, model_validator

from .base import (
    FirestoreModel,
    TimestampMixin,
    SubscriptionPlan,
    SubscriptionStatus,
    generate_entity_id,
)


# ============================================================================
# OPERATING HOURS
# ============================================================================

class DayHours(FirestoreModel):
    """Operating hours for a single day."""
    open_time: time_type = Field(default_factory=lambda: time_type(9, 0), description="Opening time")
    close_time: time_type = Field(default_factory=lambda: time_type(21, 0), description="Closing time")
    is_closed: bool = Field(default=False, description="Is closed this day")
    break_start: Optional[time_type] = Field(default=None, description="Break start time")
    break_end: Optional[time_type] = Field(default=None, description="Break end time")
    
    @model_validator(mode='after')
    def validate_times(self) -> 'DayHours':
        if not self.is_closed and self.open_time >= self.close_time:
            raise ValueError("Open time must be before close time")
        if self.break_start and self.break_end:
            if self.break_start >= self.break_end:
                raise ValueError("Break start must be before break end")
        return self
    
    def to_firestore(self) -> Dict[str, Any]:
        data = super().to_firestore()
        data['open_time'] = self.open_time.isoformat()
        data['close_time'] = self.close_time.isoformat()
        if self.break_start:
            data['break_start'] = self.break_start.isoformat()
        if self.break_end:
            data['break_end'] = self.break_end.isoformat()
        return data


class OperatingHours(FirestoreModel):
    """Weekly operating hours configuration."""
    monday: DayHours = Field(default_factory=DayHours)
    tuesday: DayHours = Field(default_factory=DayHours)
    wednesday: DayHours = Field(default_factory=DayHours)
    thursday: DayHours = Field(default_factory=DayHours)
    friday: DayHours = Field(default_factory=DayHours)
    saturday: DayHours = Field(default_factory=lambda: DayHours(
        open_time=time_type(9, 0),
        close_time=time_type(22, 0)
    ))
    sunday: DayHours = Field(default_factory=lambda: DayHours(
        open_time=time_type(10, 0),
        close_time=time_type(20, 0)
    ))
    
    def get_day_hours(self, day_name: str) -> DayHours:
        """Get operating hours for a specific day."""
        return getattr(self, day_name.lower(), DayHours())


class SalonLayout(FirestoreModel):
    """Salon physical layout configuration."""
    mens_chairs: int = Field(default=6, ge=0, description="Number of men's chairs")
    womens_chairs: int = Field(default=4, ge=0, description="Number of women's chairs")
    service_rooms: int = Field(default=4, ge=0, description="Number of service rooms")
    bridal_room: bool = Field(default=True, description="Has dedicated bridal room")
    spa_rooms: int = Field(default=1, ge=0, description="Number of spa rooms")
    waiting_capacity: int = Field(default=10, ge=1, description="Waiting area capacity")
    
    @property
    def total_stations(self) -> int:
        """Total service stations."""
        return self.mens_chairs + self.womens_chairs + self.service_rooms


# ============================================================================
# SALON BASE SCHEMA
# ============================================================================

class SalonBase(FirestoreModel, TimestampMixin):
    """Base salon schema with common fields."""
    name: str = Field(..., min_length=2, max_length=100, description="Salon name")
    slug: Optional[str] = Field(default=None, description="URL-friendly identifier")
    logo_url: Optional[str] = Field(default=None, description="Logo image URL")
    
    # Contact
    phone: str = Field(..., description="Primary phone number")
    email: Optional[str] = Field(default=None, description="Business email")
    website: Optional[str] = Field(default=None, description="Website URL")
    
    # Address
    address_line1: str = Field(..., description="Address line 1")
    address_line2: Optional[str] = Field(default=None, description="Address line 2")
    city: str = Field(..., description="City")
    state: str = Field(default="Andhra Pradesh", description="State")
    pincode: str = Field(..., description="PIN code")
    country: str = Field(default="India", description="Country")
    
    # Business
    gst_number: Optional[str] = Field(default=None, description="GST registration number")
    pan_number: Optional[str] = Field(default=None, description="PAN number")
    
    # Configuration
    operating_hours: OperatingHours = Field(default_factory=OperatingHours)
    layout: SalonLayout = Field(default_factory=SalonLayout)
    
    # Subscription
    subscription_plan: SubscriptionPlan = Field(default=SubscriptionPlan.FREE)
    subscription_status: SubscriptionStatus = Field(default=SubscriptionStatus.TRIAL)
    subscription_ends_at: Optional[datetime] = Field(default=None)
    
    # Settings
    gst_rate: Decimal = Field(default=Decimal("5.0"), description="GST percentage")
    loyalty_rate: Decimal = Field(default=Decimal("0.1"), description="Points per rupee (0.1 = 1 per 10)")
    loyalty_expiry_months: int = Field(default=12, description="Loyalty points expiry in months")
    membership_renewal_days: int = Field(default=15, description="Days before expiry to prompt renewal")
    late_arrival_grace_minutes: int = Field(default=15, description="Grace period for late arrivals")
    
    # Status
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
    
    @field_validator('gst_number')
    @classmethod
    def validate_gst(cls, v: Optional[str]) -> Optional[str]:
        if v and len(v) != 15:
            raise ValueError("GST number must be 15 characters")
        return v
    
    @field_validator('pincode')
    @classmethod
    def validate_pincode(cls, v: str) -> str:
        if not v.isdigit() or len(v) != 6:
            raise ValueError("PIN code must be 6 digits")
        return v


class SalonCreate(SalonBase):
    """Schema for creating a new salon."""
    pass


class SalonUpdate(FirestoreModel):
    """Schema for updating salon details."""
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    logo_url: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    gst_number: Optional[str] = None
    operating_hours: Optional[OperatingHours] = None
    layout: Optional[SalonLayout] = None
    gst_rate: Optional[Decimal] = None
    loyalty_rate: Optional[Decimal] = None
    loyalty_expiry_months: Optional[int] = None
    membership_renewal_days: Optional[int] = None
    late_arrival_grace_minutes: Optional[int] = None
    is_active: Optional[bool] = None


class Salon(SalonBase):
    """Complete salon schema with all fields."""
    id: str = Field(default_factory=lambda: generate_entity_id("salon"))
    owner_id: Optional[str] = Field(default=None, description="Owner user ID")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class SalonSummary(FirestoreModel):
    """Summary view of a salon for lists."""
    id: str
    name: str
    slug: Optional[str]
    city: str
    phone: str
    is_active: bool
    subscription_plan: SubscriptionPlan
    subscription_status: SubscriptionStatus


class SalonSettings(FirestoreModel, TimestampMixin):
    """Salon-specific settings and preferences."""
    salon_id: str = Field(..., description="Salon ID")
    
    # Booking settings
    booking_buffer_minutes: int = Field(default=15, description="Buffer between bookings")
    max_advance_booking_days: int = Field(default=30, description="Max days in advance for booking")
    cancellation_hours: int = Field(default=2, description="Hours before appointment for free cancellation")
    
    # Notification settings
    reminder_hours_before: int = Field(default=24, description="Hours before to send reminder")
    send_birthday_offers: bool = Field(default=True)
    send_rebooking_reminders: bool = Field(default=True)
    rebooking_days_after: int = Field(default=14, description="Days after service to prompt rebooking")
    
    # Payment settings
    accept_cash: bool = Field(default=True)
    accept_upi: bool = Field(default=True)
    accept_card: bool = Field(default=False)
    accept_wallet: bool = Field(default=False)
    
    # WhatsApp settings
    whatsapp_enabled: bool = Field(default=True)
    whatsapp_business_number: Optional[str] = Field(default=None)
    
    # Theme settings
    primary_color: str = Field(default="#6366f1")
    secondary_color: str = Field(default="#8b5cf6")
    logo_url: Optional[str] = Field(default=None)


class SalonSubscription(FirestoreModel):
    """Salon subscription details."""
    plan: SubscriptionPlan = Field(default=SubscriptionPlan.FREE)
    status: SubscriptionStatus = Field(default=SubscriptionStatus.TRIAL)
    trial_ends_at: Optional[datetime] = Field(default=None)
    current_period_start: Optional[datetime] = Field(default=None)
    current_period_end: Optional[datetime] = Field(default=None)
    cancel_at_period_end: bool = Field(default=False)
