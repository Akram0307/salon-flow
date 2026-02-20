"""
Staff schemas for Salon Flow SaaS.
Handles staff profiles, skills, availability, and scheduling.
"""
import re
from datetime import datetime, date as date_type, time as time_type
from decimal import Decimal
from typing import Optional, Dict, List, Any
from enum import Enum

from pydantic import Field, field_validator, model_validator

from .base import (
    FirestoreModel,
    TimestampMixin,
    StaffRole,
    Gender,
    ExpertiseLevel,
    SalaryType,
    generate_entity_id,
)


class ServiceSkill(FirestoreModel):
    """Staff skill for a specific service."""
    service_id: str = Field(..., description="Service ID")
    service_name: str = Field(..., description="Service name")
    expertise_level: ExpertiseLevel = Field(default=ExpertiseLevel.INTERMEDIATE)
    years_experience: int = Field(default=0, ge=0)
    is_primary: bool = Field(default=False, description="Is this a primary skill?")


class StaffSkills(FirestoreModel):
    """Collection of staff skills."""
    skills: List[ServiceSkill] = Field(default_factory=list)
    
    def get_primary_skills(self) -> List[ServiceSkill]:
        return [s for s in self.skills if s.is_primary]
    
    def get_skill_for_service(self, service_id: str) -> Optional[ServiceSkill]:
        for skill in self.skills:
            if skill.service_id == service_id:
                return skill
        return None


class ShiftPreference(FirestoreModel):
    """Staff shift preferences."""
    preferred_start_time: Optional[time_type] = Field(default=None)
    preferred_end_time: Optional[time_type] = Field(default=None)
    preferred_off_days: List[str] = Field(default_factory=list, description="Preferred off days (monday, tuesday, etc.)")
    max_consecutive_days: int = Field(default=6, ge=1)


class StaffAvailability(FirestoreModel):
    """Staff availability configuration."""
    is_available: bool = Field(default=True)
    shift_preferences: ShiftPreference = Field(default_factory=ShiftPreference)
    unavailable_dates: List[str] = Field(default_factory=list, description="Unavailable dates (ISO format)")
    max_daily_hours: int = Field(default=10, ge=1)
    min_hours_between_shifts: int = Field(default=12, ge=1)


class CommissionConfig(FirestoreModel):
    """Staff commission configuration."""
    base_commission_rate: Decimal = Field(default=Decimal("10.0"), description="Base commission percentage")
    service_commission_rates: Dict[str, Decimal] = Field(default_factory=dict, description="Service-specific rates")
    product_commission_rate: Decimal = Field(default=Decimal("5.0"))
    target_monthly_revenue: Optional[Decimal] = Field(default=None)
    bonus_threshold: Optional[Decimal] = Field(default=None)
    bonus_rate: Optional[Decimal] = Field(default=None)
    
    def to_firestore(self) -> Dict[str, Any]:
        data = super().to_firestore()
        data['base_commission_rate'] = float(self.base_commission_rate)
        data['product_commission_rate'] = float(self.product_commission_rate)
        data['service_commission_rates'] = {k: float(v) for k, v in self.service_commission_rates.items()}
        if self.target_monthly_revenue:
            data['target_monthly_revenue'] = float(self.target_monthly_revenue)
        if self.bonus_threshold:
            data['bonus_threshold'] = float(self.bonus_threshold)
        if self.bonus_rate:
            data['bonus_rate'] = float(self.bonus_rate)
        return data


class StaffBase(FirestoreModel, TimestampMixin):
    """Base staff schema."""
    salon_id: str = Field(..., description="Salon ID")
    name: str = Field(..., min_length=2, max_length=100, description="Staff name")
    phone: str = Field(..., min_length=10, max_length=15, description="Phone number (10-15 digits)")
    email: Optional[str] = Field(default=None, description="Email address")
    gender: Gender = Field(default=Gender.MALE)
    
    # Role and status
    role: StaffRole = Field(default=StaffRole.STYLIST)
    is_active: bool = Field(default=True)
    
    # Skills
    skills: StaffSkills = Field(default_factory=StaffSkills)
    
    # Availability
    availability: StaffAvailability = Field(default_factory=StaffAvailability)
    
    # Compensation
    salary_type: SalaryType = Field(default=SalaryType.COMMISSION)
    commission_config: CommissionConfig = Field(default_factory=CommissionConfig)
    
    # Dates
    joining_date: date_type = Field(default_factory=date_type.today, description="Date of joining")
    
    # Additional
    profile_image: Optional[str] = Field(default=None)
    emergency_contact: Optional[str] = Field(default=None)
    address: Optional[str] = Field(default=None)
    notes: Optional[str] = Field(default=None)



    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        """Validate phone number format."""
        # Remove any non-digit characters for validation
        digits = re.sub(r'[^0-9]', '', v)
        if len(digits) < 10 or len(digits) > 15:
            raise ValueError('Phone number must contain 10-15 digits')
        return v


class StaffCreate(StaffBase):
    """Schema for creating a new staff member."""
    salon_id: Optional[str] = Field(default=None, description="Salon ID (injected from auth context)")


class StaffUpdate(FirestoreModel):
    """Schema for updating staff details."""
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    phone: Optional[str] = None
    email: Optional[str] = None
    gender: Optional[Gender] = None
    role: Optional[StaffRole] = None
    is_active: Optional[bool] = None
    skills: Optional[StaffSkills] = None
    availability: Optional[StaffAvailability] = None
    salary_type: Optional[SalaryType] = None
    commission_config: Optional[CommissionConfig] = None
    profile_image: Optional[str] = None
    emergency_contact: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None


class Staff(StaffBase):
    """Complete staff schema."""
    id: str = Field(default_factory=lambda: generate_entity_id("staff"))
    user_id: Optional[str] = Field(default=None, description="Associated user ID for login")
    total_customers_served: int = Field(default=0)
    total_revenue_generated: Decimal = Field(default=Decimal("0"))
    average_rating: Decimal = Field(default=Decimal("0"))
    total_reviews: int = Field(default=0)
    
    def to_firestore(self) -> Dict[str, Any]:
        data = super().to_firestore()
        data['joining_date'] = self.joining_date.isoformat()
        data['total_revenue_generated'] = float(self.total_revenue_generated)
        data['average_rating'] = float(self.average_rating)
        return data


class StaffSummary(FirestoreModel):
    """Summary view of staff for lists."""
    id: str
    salon_id: str
    name: str
    role: StaffRole
    is_active: bool
    primary_skills: List[str] = Field(default_factory=list)


class StaffSchedule(FirestoreModel):
    """Staff schedule for a specific date."""
    staff_id: str
    shift_date: date_type = Field(..., description="Schedule date")
    start_time: Optional[time_type] = Field(default=None)
    end_time: Optional[time_type] = Field(default=None)
    is_off_day: bool = Field(default=False)
    is_on_leave: bool = Field(default=False)
    bookings: List[str] = Field(default_factory=list, description="Booking IDs")
    
    def to_firestore(self) -> Dict[str, Any]:
        data = super().to_firestore()
        data['shift_date'] = self.shift_date.isoformat()
        if self.start_time:
            data['start_time'] = self.start_time.isoformat()
        if self.end_time:
            data['end_time'] = self.end_time.isoformat()
        return data


class StaffSearch(FirestoreModel):
    """Search parameters for staff."""
    salon_id: str
    role: Optional[StaffRole] = None
    is_active: Optional[bool] = None
    skill_service_id: Optional[str] = None
    available_on: Optional[date_type] = None

# Alias for backward compatibility
StaffSkill = ServiceSkill
