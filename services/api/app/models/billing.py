"""Firestore Models for Enhanced Billing System"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional
from google.cloud.firestore import SERVER_TIMESTAMP
from app.models.base import FirestoreBase


class PriceOverrideModel(FirestoreBase):
    """Model for price override logs"""
    
    collection_name = "price_overrides"
    id_field = "override_id"
    
    # Override details
    salon_id: str
    booking_id: str
    service_id: str
    service_name: str
    original_price: Decimal
    new_price: Decimal
    discount_percent: Decimal
    
    # Reason tracking
    reason_code: str  # loyalty, service_recovery, promotion, staff_suggestion, price_match, custom
    reason_text: Optional[str] = None
    
    # Staff suggestion reference
    suggestion_id: Optional[str] = None
    suggested_by: Optional[str] = None  # staff_id
    
    # Approval tracking
    approved_by: str  # manager_id or owner_id
    approved_at: datetime
    
    # Timestamps
    created_at: datetime
    
    class Config:
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat()
        }
    
    @classmethod
    def calculate_discount_percent(cls, original: Decimal, new: Decimal) -> Decimal:
        """Calculate discount percentage"""
        if original <= 0:
            return Decimal('0')
        return ((original - new) / original) * 100


class StaffSuggestionModel(FirestoreBase):
    """Model for staff price suggestions"""
    
    collection_name = "staff_suggestions"
    id_field = "suggestion_id"
    
    # Suggestion details
    salon_id: str
    booking_id: str
    staff_id: str
    staff_name: str
    
    # Suggestion type and details
    suggestion_type: str  # discount, complimentary, upgrade, custom
    service_id: Optional[str] = None
    service_name: Optional[str] = None
    original_price: Decimal = Decimal('0')
    suggested_price: Decimal = Decimal('0')
    discount_percent: Decimal = Decimal('0')
    
    # Reason
    reason: str
    
    # Status tracking
    status: str = "pending"  # pending, approved, rejected, expired
    
    # Review tracking
    reviewed_by: Optional[str] = None  # manager_id
    reviewed_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    
    # Timestamps
    created_at: datetime
    expires_at: datetime
    
    class Config:
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat()
        }
    
    @classmethod
    def create_with_expiry(cls, expiry_minutes: int = 30, **kwargs):
        """Create suggestion with auto-expiry"""
        now = datetime.utcnow()
        kwargs['created_at'] = now
        kwargs['expires_at'] = now + timedelta(minutes=expiry_minutes)
        return cls(**kwargs)


class ApprovalRulesModel(FirestoreBase):
    """Model for salon-specific approval rules"""
    
    collection_name = "approval_rules"
    id_field = "rules_id"
    
    salon_id: str
    
    # Discount thresholds (percentages)
    auto_approve_threshold: Decimal = Decimal('10')  # Auto-approve up to 10%
    manager_approval_threshold: Decimal = Decimal('20')  # Manager needed for 10-20%
    owner_approval_threshold: Decimal = Decimal('30')  # Owner needed for >20%
    
    # Limits
    max_discount_per_day: Decimal = Decimal('10000')  # Max total discount per day
    
    # Settings
    require_reason_for_discount: bool = True
    allow_staff_suggestions: bool = True
    suggestion_expiry_minutes: int = 30
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    class Config:
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat()
        }


class BillModel(FirestoreBase):
    """Model for generated bills"""
    
    collection_name = "bills"
    id_field = "bill_id"
    
    # Bill identification
    salon_id: str
    booking_id: str
    invoice_number: str
    
    # Customer info
    customer_id: str
    customer_name: str
    customer_phone: str
    
    # Services (stored as list of dicts)
    services: list  # List of BillingServiceItem dicts
    
    # Pricing
    subtotal: Decimal
    membership_discount: Decimal = Decimal('0')
    membership_discount_percent: Decimal = Decimal('0')
    manual_adjustment: Decimal = Decimal('0')
    manual_adjustment_reason: Optional[str] = None
    
    # Tax
    gst_percent: Decimal = Decimal('5')
    gst_amount: Decimal
    
    # Final
    grand_total: Decimal
    
    # Payment
    payment_method: str  # cash, upi, card, wallet
    amount_received: Decimal
    change_due: Decimal = Decimal('0')
    
    # Loyalty
    loyalty_points_earned: int = 0
    loyalty_points_redeemed: int = 0
    
    # Override references
    override_ids: list = []  # List of override IDs applied
    
    # Timestamps
    created_at: datetime
    created_by: str  # staff_id or manager_id
    
    class Config:
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat()
        }
    
    @classmethod
    def generate_invoice_number(cls, salon_id: str, sequence: int) -> str:
        """Generate invoice number: INV-{SALON_PREFIX}-{YYYY}-{SEQUENCE}"""
        from datetime import datetime
        year = datetime.utcnow().year
        salon_prefix = salon_id[:4].upper()
        return f"INV-{salon_prefix}-{year}-{sequence:06d}"


class DailyDiscountTracker(FirestoreBase):
    """Track daily discount totals for approval rules"""
    
    collection_name = "daily_discount_tracker"
    id_field = "tracker_id"
    
    salon_id: str
    date: str  # YYYY-MM-DD format
    total_discount: Decimal = Decimal('0')
    override_count: int = 0
    updated_at: datetime
    
    class Config:
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat()
        }
    
    @classmethod
    def get_tracker_id(cls, salon_id: str, date: str) -> str:
        return f"{salon_id}_{date}"
