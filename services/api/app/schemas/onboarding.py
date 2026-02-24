"""Onboarding schemas for Salon Flow SaaS.
Handles salon onboarding flow, invite codes, and setup progress.
"""
from datetime import datetime, date as date_type, time as time_type
from decimal import Decimal
from typing import Optional, Dict, List, Any
from enum import Enum

from pydantic import Field, field_validator, model_validator, EmailStr

from .base import (
    FirestoreModel,
    TimestampMixin,
    SubscriptionPlan,
    SubscriptionStatus,
    StaffRole,
    generate_entity_id,
)
from .salon import DayHours, OperatingHours, SalonLayout


class OnboardingStep(str, Enum):
    """Onboarding steps enumeration."""
    CREATE_SALON = "create_salon"
    CONFIGURE_LAYOUT = "configure_layout"
    ADD_SERVICES = "add_services"
    ADD_STAFF = "add_staff"
    SET_BUSINESS_HOURS = "set_business_hours"
    COMPLETE = "complete"


class OnboardingStatus(str, Enum):
    """Onboarding status enumeration."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class SalonCreateRequest(FirestoreModel):
    """Request schema for creating a new salon during onboarding."""
    name: str = Field(..., min_length=2, max_length=100, description="Salon name")
    phone: str = Field(..., min_length=10, max_length=15, description="Primary phone number")
    email: Optional[EmailStr] = Field(default=None, description="Business email")
    
    # Address
    address_line1: str = Field(..., description="Address line 1")
    address_line2: Optional[str] = Field(default=None, description="Address line 2")
    city: str = Field(default="Kurnool", description="City")
    state: str = Field(default="Andhra Pradesh", description="State")
    pincode: str = Field(..., description="PIN code (6 digits)")
    
    # Business details
    gst_number: Optional[str] = Field(default=None, description="GST registration number")
    pan_number: Optional[str] = Field(default=None, description="PAN number")
    
    # Owner details
    owner_name: str = Field(..., min_length=2, max_length=100, description="Owner's full name")
    owner_phone: str = Field(..., min_length=10, max_length=15, description="Owner's phone number")
    owner_email: EmailStr = Field(..., description="Owner's email address")
    owner_password: str = Field(..., min_length=6, description="Owner's password")
    
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


class LayoutConfigRequest(FirestoreModel):
    """Request schema for configuring salon layout."""
    mens_chairs: int = Field(default=6, ge=0, description="Number of men's chairs")
    womens_chairs: int = Field(default=4, ge=0, description="Number of women's chairs")
    service_rooms: int = Field(default=4, ge=0, description="Number of service rooms")
    bridal_room: bool = Field(default=True, description="Has dedicated bridal room")
    spa_rooms: int = Field(default=1, ge=0, description="Number of spa rooms")
    waiting_capacity: int = Field(default=10, ge=1, description="Waiting area capacity")


class BusinessHoursRequest(FirestoreModel):
    """Request schema for setting business hours."""
    monday: Optional[DayHours] = None
    tuesday: Optional[DayHours] = None
    wednesday: Optional[DayHours] = None
    thursday: Optional[DayHours] = None
    friday: Optional[DayHours] = None
    saturday: Optional[DayHours] = None
    sunday: Optional[DayHours] = None
    
    def to_operating_hours(self) -> OperatingHours:
        """Convert to OperatingHours schema."""
        default_hours = DayHours()
        return OperatingHours(
            monday=self.monday or default_hours,
            tuesday=self.tuesday or default_hours,
            wednesday=self.wednesday or default_hours,
            thursday=self.thursday or default_hours,
            friday=self.friday or default_hours,
            saturday=self.saturday or DayHours(
                open_time=time_type(9, 0),
                close_time=time_type(22, 0)
            ),
            sunday=self.sunday or DayHours(
                open_time=time_type(10, 0),
                close_time=time_type(20, 0)
            ),
        )


class ServiceImportRequest(FirestoreModel):
    """Request schema for importing services from template."""
    template_type: str = Field(default="salon", description="Template type: salon, spa, unisex")
    categories: Optional[List[str]] = Field(default=None, description="Specific categories to import")
    custom_services: Optional[List[Dict[str, Any]]] = Field(default=None, description="Custom services to add")


class StaffInviteRequest(FirestoreModel):
    """Request schema for inviting staff during onboarding."""
    name: str = Field(..., min_length=2, max_length=100, description="Staff name")
    phone: str = Field(..., min_length=10, max_length=15, description="Phone number")
    email: Optional[EmailStr] = Field(default=None, description="Email address")
    role: StaffRole = Field(default=StaffRole.STYLIST, description="Staff role")
    specializations: Optional[List[str]] = Field(default=None, description="Service specializations")


class JoinSalonRequest(FirestoreModel):
    """Request schema for joining an existing salon."""
    invite_code: str = Field(..., min_length=6, max_length=10, description="Salon invite code")
    name: str = Field(..., min_length=2, max_length=100, description="Staff name")
    phone: str = Field(..., min_length=10, max_length=15, description="Phone number")
    email: Optional[EmailStr] = Field(default=None, description="Email address")
    password: str = Field(..., min_length=6, description="Password")


class OnboardingProgress(FirestoreModel, TimestampMixin):
    """Onboarding progress tracking."""
    salon_id: str = Field(..., description="Salon ID")
    current_step: OnboardingStep = Field(default=OnboardingStep.CREATE_SALON, description="Current step")
    status: OnboardingStatus = Field(default=OnboardingStatus.NOT_STARTED, description="Overall status")
    
    # Step completion flags
    salon_created: bool = Field(default=False)
    layout_configured: bool = Field(default=False)
    services_added: bool = Field(default=False)
    staff_added: bool = Field(default=False)
    business_hours_set: bool = Field(default=False)
    
    # Metadata
    completed_steps: List[str] = Field(default_factory=list)
    skipped_steps: List[str] = Field(default_factory=list)
    
    # Counts
    services_count: int = Field(default=0)
    staff_count: int = Field(default=0)
    
    def get_completion_percentage(self) -> int:
        """Calculate onboarding completion percentage."""
        total_steps = 5
        completed = sum([
            self.salon_created,
            self.layout_configured,
            self.services_added,
            self.staff_added,
            self.business_hours_set,
        ])
        return int((completed / total_steps) * 100)
    
    def get_next_step(self) -> Optional[OnboardingStep]:
        """Get the next incomplete step."""
        if not self.salon_created:
            return OnboardingStep.CREATE_SALON
        if not self.layout_configured:
            return OnboardingStep.CONFIGURE_LAYOUT
        if not self.services_added:
            return OnboardingStep.ADD_SERVICES
        if not self.staff_added:
            return OnboardingStep.ADD_STAFF
        if not self.business_hours_set:
            return OnboardingStep.SET_BUSINESS_HOURS
        return OnboardingStep.COMPLETE


class OnboardingState(FirestoreModel):
    """Complete onboarding state for a salon."""
    id: str = Field(default_factory=lambda: generate_entity_id("onboard"))
    salon_id: str = Field(..., description="Salon ID")
    progress: OnboardingProgress = Field(default_factory=lambda: OnboardingProgress(salon_id=""))
    invite_code: str = Field(..., description="Unique invite code for staff")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)


class OnboardingResponse(FirestoreModel):
    """Response schema for onboarding operations."""
    success: bool = Field(default=True)
    message: str = Field(default="Operation successful")
    salon_id: Optional[str] = None
    invite_code: Optional[str] = None
    progress: Optional[OnboardingProgress] = None
    next_step: Optional[str] = None
    completion_percentage: int = Field(default=0)


class InviteCodeInfo(FirestoreModel):
    """Information about an invite code."""
    invite_code: str
    salon_id: str
    salon_name: str
    salon_city: str
    is_valid: bool = True
    expires_at: Optional[datetime] = None


__all__ = [
    "OnboardingStep",
    "OnboardingStatus",
    "SalonCreateRequest",
    "LayoutConfigRequest",
    "BusinessHoursRequest",
    "ServiceImportRequest",
    "StaffInviteRequest",
    "JoinSalonRequest",
    "OnboardingProgress",
    "OnboardingState",
    "OnboardingResponse",
    "InviteCodeInfo",
]
