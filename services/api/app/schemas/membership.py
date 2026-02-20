"""
Membership schemas for Salon Flow SaaS.
Handles membership plans, subscriptions, and renewals.
"""
from datetime import datetime, date as date_type, time as time_type
from decimal import Decimal
from typing import Optional, Dict, List, Any
from enum import Enum

from pydantic import Field, field_validator, field_validator, model_validator

from .base import (
    FirestoreModel,
    TimestampMixin,
    MembershipPlanType,
    MembershipStatus,
    generate_entity_id,
)


class MembershipPlanBenefits(FirestoreModel):
    """Benefits included in a membership plan."""
    discount_percentage: Decimal = Field(default=Decimal("10.0"), description="Discount on services")
    free_services_per_month: int = Field(default=0)
    priority_booking: bool = Field(default=False)
    birthday_bonus_points: int = Field(default=100)
    complimentary_services: List[str] = Field(default_factory=list)
    exclusive_access: bool = Field(default=False)
    
    def to_firestore(self) -> Dict[str, Any]:
        data = super().to_firestore()
        data['discount_percentage'] = float(self.discount_percentage)
        return data


class MembershipPlanPricing(FirestoreModel):
    """Pricing for a membership plan."""
    monthly_price: Decimal = Field(default=Decimal("0"))
    quarterly_price: Decimal = Field(default=Decimal("0"))
    annual_price: Decimal = Field(default=Decimal("0"))
    setup_fee: Decimal = Field(default=Decimal("0"))
    
    def to_firestore(self) -> Dict[str, Any]:
        data = super().to_firestore()
        data['monthly_price'] = float(self.monthly_price)
        data['quarterly_price'] = float(self.quarterly_price)
        data['annual_price'] = float(self.annual_price)
        data['setup_fee'] = float(self.setup_fee)
        return data


class MembershipPlan(FirestoreModel, TimestampMixin):
    """Membership plan template."""
    id: str = Field(default_factory=lambda: generate_entity_id("plan"))
    salon_id: str = Field(..., description="Salon ID")
    name: str = Field(..., min_length=2, max_length=50, description="Plan name")
    description: Optional[str] = Field(default=None)
    plan_type: MembershipPlanType = Field(default=MembershipPlanType.MONTHLY)
    pricing: MembershipPlanPricing = Field(default_factory=MembershipPlanPricing)
    benefits: MembershipPlanBenefits = Field(default_factory=MembershipPlanBenefits)
    is_active: bool = Field(default=True)
    max_members: Optional[int] = Field(default=None, description="Max members allowed")
    current_members: int = Field(default=0)


class MembershipUsage(FirestoreModel):
    """Membership usage tracking."""
    services_used: int = Field(default=0)
    services_limit: Optional[int] = Field(default=None)
    discount_used: Decimal = Field(default=Decimal("0"))
    free_services_used: int = Field(default=0)
    last_used_date: Optional[date_type] = Field(default=None)
    
    @property
    def has_services_remaining(self) -> bool:
        if self.services_limit is None:
            return True
        return self.services_used < self.services_limit
    
    def to_firestore(self) -> Dict[str, Any]:
        data = super().to_firestore()
        data['discount_used'] = float(self.discount_used)
        if self.last_used_date:
            data['last_used_date'] = self.last_used_date.isoformat()
        return data


class MembershipBase(FirestoreModel, TimestampMixin):
    """Base membership schema."""
    salon_id: str = Field(..., description="Salon ID")
    customer_id: str = Field(..., description="Customer ID")
    plan_id: str = Field(..., description="Membership plan ID")
    plan_name: str = Field(..., description="Plan name")
    plan_type: MembershipPlanType = Field(default=MembershipPlanType.MONTHLY)
    
    # Dates
    start_date: date_type = Field(..., description="Membership start date")
    end_date: date_type = Field(..., description="Membership end date")
    renewal_date: Optional[date_type] = Field(default=None, description="Renewal reminder date")
    
    # Payment
    amount_paid: Decimal = Field(..., description="Amount paid for membership")
    discount_rate: Decimal = Field(default=Decimal("10.0"), description="Discount rate")

    @field_validator('amount_paid')
    @classmethod
    def validate_amount_paid(cls, v: Decimal) -> Decimal:
        """Ensure amount paid is non-negative."""
        if v < 0:
            raise ValueError('Amount paid must be non-negative')
        return v
    
    # Status
    status: MembershipStatus = Field(default=MembershipStatus.ACTIVE)
    auto_renew: bool = Field(default=False)
    
    # Usage
    usage: MembershipUsage = Field(default_factory=MembershipUsage)
    
    @model_validator(mode='after')
    def validate_dates(self) -> 'MembershipBase':
        if self.start_date >= self.end_date:
            raise ValueError("Start date must be before end date")
        return self
    
    @property
    def days_remaining(self) -> int:
        today = date_type.today()
        if self.end_date < today:
            return 0
        return (self.end_date - today).days
    
    @property
    def is_expiring_soon(self) -> bool:
        return self.days_remaining <= 15
    
    def to_firestore(self) -> Dict[str, Any]:
        data = super().to_firestore()
        data['start_date'] = self.start_date.isoformat()
        data['end_date'] = self.end_date.isoformat()
        if self.renewal_date:
            data['renewal_date'] = self.renewal_date.isoformat()
        data['amount_paid'] = float(self.amount_paid)
        data['discount_rate'] = float(self.discount_rate)
        return data


class MembershipCreate(FirestoreModel):
    """Schema for creating a membership."""
    salon_id: str = Field(default="", description="Reference to the salon (injected from auth)")
    customer_id: str = Field(..., description="Customer ID")
    plan_id: str = Field(..., description="Membership plan ID")
    plan_name: str = Field(..., description="Plan name")
    plan_type: MembershipPlanType = Field(default=MembershipPlanType.MONTHLY)
    
    # Dates - start_date optional (defaults to today), end_date calculated from duration
    start_date: Optional[date_type] = Field(default=None, description="Membership start date (defaults to today)")
    end_date: Optional[date_type] = Field(default=None, description="Membership end date (calculated from duration)")
    
    # Duration in months (used to calculate end_date)
    duration_months: int = Field(default=1, ge=1, le=36, description="Membership duration in months")
    
    # Payment
    amount_paid: Decimal = Field(..., description="Amount paid for membership")
    discount_rate: Decimal = Field(default=Decimal("10.0"), description="Discount rate")

    @field_validator('amount_paid')
    @classmethod
    def validate_amount_paid(cls, v: Decimal) -> Decimal:
        """Ensure amount paid is non-negative."""
        if v < 0:
            raise ValueError('Amount paid must be non-negative')
        return v


class MembershipUpdate(FirestoreModel):
    """Schema for updating a membership."""
    status: Optional[MembershipStatus] = None
    auto_renew: Optional[bool] = None
    end_date: Optional[date_type] = None
    renewal_date: Optional[date_type] = None
    notes: Optional[str] = None


class MembershipRenewal(FirestoreModel):
    """Schema for membership renewal."""
    membership_id: str
    new_start_date: date_type
    new_end_date: date_type
    amount_paid: Decimal
    plan_type: Optional[MembershipPlanType] = None
    
    def to_firestore(self) -> Dict[str, Any]:
        data = super().to_firestore()
        data['new_start_date'] = self.new_start_date.isoformat()
        data['new_end_date'] = self.new_end_date.isoformat()
        data['amount_paid'] = float(self.amount_paid)
        return data


class Membership(MembershipBase):
    """Complete membership schema."""
    id: str = Field(default_factory=lambda: generate_entity_id("membership"))
    payment_id: Optional[str] = Field(default=None, description="Associated payment ID")
    
    def renew(self, new_end_date: date_type, amount_paid: Decimal) -> None:
        """Renew membership."""
        self.end_date = new_end_date
        self.amount_paid = amount_paid
        self.status = MembershipStatus.ACTIVE
        self.usage = MembershipUsage()


class MembershipSummary(FirestoreModel):
    """Summary view of a membership."""
    id: str
    salon_id: str
    customer_id: str
    plan_name: str
    plan_type: MembershipPlanType
    start_date: date_type
    end_date: date_type
    status: MembershipStatus
    days_remaining: int


class MembershipStats(FirestoreModel):
    """Membership statistics."""
    total_memberships: int = Field(default=0)
    active_memberships: int = Field(default=0)
    expiring_soon: int = Field(default=0)
    total_revenue: Decimal = Field(default=Decimal("0"))
    by_plan_type: Dict[str, int] = Field(default_factory=dict)
    
    def to_firestore(self) -> Dict[str, Any]:
        data = super().to_firestore()
        data['total_revenue'] = float(self.total_revenue)
        return data

# Alias for backward compatibility
MembershipType = MembershipPlanType
