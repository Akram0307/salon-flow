"""Enhanced Billing Schemas with Price Override and Staff Suggestions"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class OverrideReasonCode(str, Enum):
    """Reason codes for price overrides"""
    LOYALTY = "loyalty"
    SERVICE_RECOVERY = "service_recovery"
    PROMOTION = "promotion"
    STAFF_SUGGESTION = "staff_suggestion"
    PRICE_MATCH = "price_match"
    CUSTOM = "custom"


class SuggestionType(str, Enum):
    """Types of staff suggestions"""
    DISCOUNT = "discount"
    COMPLIMENTARY = "complimentary"
    UPGRADE = "upgrade"
    CUSTOM = "custom"


class SuggestionStatus(str, Enum):
    """Status of staff suggestions"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


# ============== Price Override Schemas ==============

class PriceOverrideBase(BaseModel):
    """Base schema for price override"""
    service_id: str = Field(..., description="ID of the service being overridden")
    service_name: str = Field(..., description="Name of the service")
    original_price: Decimal = Field(..., gt=0, description="Original price of the service")
    new_price: Decimal = Field(..., ge=0, description="New overridden price")
    reason_code: OverrideReasonCode = Field(..., description="Reason for override")
    reason_text: Optional[str] = Field(None, description="Additional reason details")
    suggested_by: Optional[str] = Field(None, description="Staff ID if this was a suggestion")

    @field_validator('new_price')
    @classmethod
    def validate_new_price(cls, v, info):
        """Ensure new price is not greater than original (no markup)"""
        original = info.data.get('original_price')
        if original and v > original:
            raise ValueError('Override price cannot be greater than original price')
        return v


class PriceOverrideCreate(PriceOverrideBase):
    """Schema for creating a price override"""
    booking_id: str = Field(..., description="Booking ID this override applies to")


class PriceOverrideInDB(PriceOverrideBase):
    """Schema for price override in database"""
    id: str
    salon_id: str
    booking_id: str
    discount_percent: Decimal = Field(..., description="Calculated discount percentage")
    approved_by: str = Field(..., description="Manager/Owner ID who approved")
    approved_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class PriceOverrideResponse(PriceOverrideInDB):
    """Response schema for price override"""
    approver_name: Optional[str] = Field(None, description="Name of approver")
    suggester_name: Optional[str] = Field(None, description="Name of staff who suggested")


class PriceOverrideListResponse(BaseModel):
    """Paginated list of price overrides"""
    items: List[PriceOverrideResponse]
    total: int
    page: int
    page_size: int
    total_discount: Decimal = Field(..., description="Total discount amount across all items")


# ============== Staff Suggestion Schemas ==============

class StaffSuggestionBase(BaseModel):
    """Base schema for staff suggestions"""
    booking_id: str = Field(..., description="Booking ID this suggestion applies to")
    suggestion_type: SuggestionType = Field(..., description="Type of suggestion")
    service_id: Optional[str] = Field(None, description="Service ID if applicable")
    service_name: Optional[str] = Field(None, description="Service name if applicable")
    original_price: Decimal = Field(default=Decimal('0'), ge=0, description="Original price")
    suggested_price: Decimal = Field(default=Decimal('0'), ge=0, description="Suggested price")
    discount_percent: Decimal = Field(default=Decimal('0'), ge=0, le=100, description="Discount percentage")
    reason: str = Field(..., min_length=10, max_length=500, description="Reason for suggestion")


class StaffSuggestionCreate(StaffSuggestionBase):
    """Schema for creating a staff suggestion"""
    pass


class StaffSuggestionInDB(StaffSuggestionBase):
    """Schema for staff suggestion in database"""
    id: str
    salon_id: str
    staff_id: str
    staff_name: str
    status: SuggestionStatus = SuggestionStatus.PENDING
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    created_at: datetime
    expires_at: datetime

    class Config:
        from_attributes = True


class StaffSuggestionResponse(StaffSuggestionInDB):
    """Response schema for staff suggestion"""
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    impact_amount: Decimal = Field(..., description="Financial impact of suggestion")


class StaffSuggestionListResponse(BaseModel):
    """Paginated list of staff suggestions"""
    items: List[StaffSuggestionResponse]
    total: int
    pending_count: int
    approved_count: int
    rejected_count: int


class SuggestionApproval(BaseModel):
    """Schema for approving/rejecting a suggestion"""
    approved: bool = Field(..., description="Whether to approve or reject")
    rejection_reason: Optional[str] = Field(None, description="Reason if rejected")


# ============== Billing Schemas ==============

class BillingServiceItem(BaseModel):
    """Service item in a bill"""
    service_id: str
    service_name: str
    staff_id: str
    staff_name: str
    original_price: Decimal
    override_price: Optional[Decimal] = None
    override_id: Optional[str] = None
    quantity: int = Field(default=1, ge=1)

    @property
    def final_price(self) -> Decimal:
        return self.override_price if self.override_price else self.original_price


class BillingCreate(BaseModel):
    """Schema for creating a bill"""
    booking_id: str
    services: List[BillingServiceItem]
    membership_discount_percent: Decimal = Field(default=Decimal('0'), ge=0, le=100)
    manual_adjustment: Decimal = Field(default=Decimal('0'))
    manual_adjustment_reason: Optional[str] = None
    payment_method: str = Field(..., description="cash, upi, card, wallet")
    amount_received: Decimal = Field(..., ge=0)


class BillResponse(BaseModel):
    """Response schema for generated bill"""
    id: str
    salon_id: str
    booking_id: str
    invoice_number: str
    customer_name: str
    customer_phone: str
    services: List[BillingServiceItem]
    subtotal: Decimal
    membership_discount: Decimal
    manual_adjustment: Decimal
    gst_amount: Decimal
    gst_percent: Decimal = Field(default=Decimal('5'))
    grand_total: Decimal
    payment_method: str
    amount_received: Decimal
    change_due: Decimal
    loyalty_points_earned: int
    created_at: datetime
    created_by: str


# ============== Approval Rules Schemas ==============

class ApprovalRulesBase(BaseModel):
    """Base schema for approval rules"""
    auto_approve_threshold: Decimal = Field(default=Decimal('10'), ge=0, le=100)
    manager_approval_threshold: Decimal = Field(default=Decimal('20'), ge=0, le=100)
    owner_approval_threshold: Decimal = Field(default=Decimal('30'), ge=0, le=100)
    max_discount_per_day: Decimal = Field(default=Decimal('10000'), ge=0)
    require_reason_for_discount: bool = Field(default=True)
    allow_staff_suggestions: bool = Field(default=True)
    suggestion_expiry_minutes: int = Field(default=30, ge=5, le=120)


class ApprovalRulesCreate(ApprovalRulesBase):
    """Schema for creating approval rules"""
    pass


class ApprovalRulesResponse(ApprovalRulesBase):
    """Response schema for approval rules"""
    id: str
    salon_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
