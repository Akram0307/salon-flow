"""
Customer schemas for Salon Flow SaaS.
Handles customer profiles, loyalty points, and membership tracking.
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Dict, List, Any

from pydantic import Field, field_validator, model_validator

from .base import (
    FirestoreModel,
    TimestampMixin,
    Gender,
    MembershipStatus,
    BusinessConstants,
    generate_entity_id,
)


# ============================================================================
# CUSTOMER PREFERENCES
# ============================================================================

class CustomerPreferences(FirestoreModel):
    """Customer service preferences."""
    preferred_stylist_id: Optional[str] = Field(default=None, description="Preferred staff member")
    preferred_services: List[str] = Field(default_factory=list, description="List of preferred service IDs")
    preferred_time_slots: List[str] = Field(default_factory=list, description="Preferred booking times")
    preferred_products: List[str] = Field(default_factory=list, description="Preferred product IDs")
    communication_preference: str = Field(default="whatsapp", description="Preferred communication channel")
    reminder_preference: str = Field(default="both", description="sms, whatsapp, email, or both")
    language_preference: str = Field(default="en", description="Preferred language code")
    receive_promotions: bool = Field(default=True, description="Opt-in for promotional messages")
    receive_reminders: bool = Field(default=True, description="Opt-in for appointment reminders")
    notes_on_service: Optional[str] = Field(default=None, description="Special notes for service")


class CustomerAddress(FirestoreModel):
    """Customer address details."""
    line1: Optional[str] = Field(default=None, max_length=100, description="Address line 1")
    line2: Optional[str] = Field(default=None, max_length=100, description="Address line 2")
    city: Optional[str] = Field(default=None, max_length=50, description="City")
    state: Optional[str] = Field(default=None, max_length=50, description="State")
    pincode: Optional[str] = Field(default=None, max_length=6, description="PIN code")
    landmark: Optional[str] = Field(default=None, max_length=50, description="Nearby landmark")


# ============================================================================
# CUSTOMER SCHEMAS
# ============================================================================

class CustomerBase(FirestoreModel, TimestampMixin):
    """Base customer schema with common fields."""
    salon_id: str = Field(..., description="Reference to the salon")
    name: str = Field(..., min_length=2, max_length=100, description="Customer full name")
    phone: str = Field(..., min_length=10, max_length=15, description="Primary phone number")
    email: Optional[str] = Field(default=None, max_length=100, description="Email address")
    gender: Gender = Field(default=Gender.OTHER, description="Gender")
    
    # Personal dates
    date_of_birth: Optional[date] = Field(default=None, description="Date of birth")
    anniversary_date: Optional[date] = Field(default=None, description="Anniversary date")
    
    # Address
    address: Optional[CustomerAddress] = Field(default=None, description="Customer address")
    
    # Preferences
    preferences: CustomerPreferences = Field(default_factory=CustomerPreferences, description="Service preferences")
    
    # Loyalty
    loyalty_points_balance: int = Field(default=0, ge=0, description="Current loyalty points balance")
    loyalty_points_earned: int = Field(default=0, ge=0, description="Total points earned")
    loyalty_points_redeemed: int = Field(default=0, ge=0, description="Total points redeemed")
    loyalty_points_expired: int = Field(default=0, ge=0, description="Total points expired")
    
    # Membership
    membership_id: Optional[str] = Field(default=None, description="Active membership ID")
    membership_status: MembershipStatus = Field(default=MembershipStatus.PENDING, description="Membership status")
    
    # Visit tracking
    total_visits: int = Field(default=0, ge=0, description="Total number of visits")
    total_spent: Decimal = Field(default=Decimal("0"), ge=0, description="Total amount spent")
    first_visit: Optional[datetime] = Field(default=None, description="First visit datetime")
    last_visit: Optional[datetime] = Field(default=None, description="Last visit datetime")
    
    # Notes and tags
    notes: Optional[str] = Field(default=None, max_length=500, description="Staff notes about customer")
    tags: List[str] = Field(default_factory=list, description="Customer tags for segmentation")
    
    # Status
    is_active: bool = Field(default=True, description="Whether customer is active")
    is_blacklisted: bool = Field(default=False, description="Whether customer is blacklisted")
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate phone number format."""
        cleaned = v.replace(' ', '').replace('-', '').replace('+', '')
        if not cleaned.isdigit():
            raise ValueError("Phone number must contain only digits")
        if len(cleaned) < 10:
            raise ValueError("Phone number must be at least 10 digits")
        return cleaned[-10:]  # Store last 10 digits
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        """Validate email format."""
        if v is None:
            return v
        if '@' not in v or '.' not in v.split('@')[-1]:
            raise ValueError("Invalid email format")
        return v.lower()
    
    @property
    def average_spending(self) -> Decimal:
        """Calculate average spending per visit."""
        if self.total_visits == 0:
            return Decimal("0")
        return (self.total_spent / self.total_visits).quantize(Decimal('0.01'))
    
    @property
    def loyalty_points_value(self) -> Decimal:
        """Calculate monetary value of loyalty points."""
        return Decimal(self.loyalty_points_balance) * Decimal("1.00")
    
    @property
    def is_member(self) -> bool:
        """Check if customer has active membership."""
        return self.membership_status == MembershipStatus.ACTIVE
    
    @property
    def is_new_customer(self) -> bool:
        """Check if customer is new (first visit within last 30 days)."""
        if not self.first_visit:
            return True
        from datetime import timedelta
        return (datetime.utcnow() - self.first_visit) < timedelta(days=30)


class CustomerCreate(CustomerBase):
    """Schema for creating a new customer."""
    customer_id: str = Field(default_factory=lambda: generate_entity_id("cust"))
    salon_id: Optional[str] = Field(default=None, description="Will be set from auth context")
    
    @model_validator(mode='after')
    def set_first_visit(self) -> 'CustomerCreate':
        if self.first_visit is None:
            self.first_visit = datetime.utcnow()
        return self


class CustomerUpdate(FirestoreModel):
    """Schema for updating customer information."""
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    phone: Optional[str] = Field(default=None, min_length=10, max_length=15)
    email: Optional[str] = Field(default=None, max_length=100)
    gender: Optional[Gender] = Field(default=None)
    date_of_birth: Optional[date] = Field(default=None)
    anniversary_date: Optional[date] = Field(default=None)
    address: Optional[CustomerAddress] = Field(default=None)
    preferences: Optional[CustomerPreferences] = Field(default=None)
    membership_id: Optional[str] = Field(default=None)
    membership_status: Optional[MembershipStatus] = Field(default=None)
    notes: Optional[str] = Field(default=None, max_length=500)
    tags: Optional[List[str]] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)
    is_blacklisted: Optional[bool] = Field(default=None)


class Customer(CustomerBase):
    """Complete customer entity with all fields."""
    customer_id: str = Field(..., description="Unique customer identifier")
    
    # Firebase Auth UID (if registered)
    user_id: Optional[str] = Field(default=None, description="Firebase Auth UID")
    
    # Computed fields
    last_booking_id: Optional[str] = Field(default=None, description="Last booking ID")
    last_service_name: Optional[str] = Field(default=None, description="Last service taken")
    last_staff_name: Optional[str] = Field(default=None, description="Last staff member served")
    
    # Birthday/Anniversary reminders
    birthday_reminder_sent: bool = Field(default=False, description="Birthday reminder sent this year")
    anniversary_reminder_sent: bool = Field(default=False, description="Anniversary reminder sent this year")
    
    # Referral tracking
    referred_by: Optional[str] = Field(default=None, description="Customer ID who referred")
    referral_count: int = Field(default=0, ge=0, description="Number of customers referred")
    referral_earned_points: int = Field(default=0, ge=0, description="Points earned from referrals")
    
    def add_loyalty_points(self, points: int) -> None:
        """Add loyalty points to customer balance."""
        self.loyalty_points_balance += points
        self.loyalty_points_earned += points
    
    def redeem_loyalty_points(self, points: int) -> bool:
        """Redeem loyalty points from customer balance.
        
        Returns:
            True if redemption successful, False if insufficient balance
        """
        if points > self.loyalty_points_balance:
            return False
        self.loyalty_points_balance -= points
        self.loyalty_points_redeemed += points
        return True
    
    def record_visit(self, amount: Decimal) -> None:
        """Record a customer visit and spending."""
        self.total_visits += 1
        self.total_spent += amount
        self.last_visit = datetime.utcnow()
        if self.first_visit is None:
            self.first_visit = datetime.utcnow()
    
    def to_firestore(self) -> Dict[str, Any]:
        """Convert to Firestore-compatible dictionary."""
        data = super().to_firestore()
        # Convert Decimal to float
        data['total_spent'] = float(self.total_spent)
        # Convert dates to ISO strings
        if self.date_of_birth:
            data['date_of_birth'] = self.date_of_birth.isoformat()
        if self.anniversary_date:
            data['anniversary_date'] = self.anniversary_date.isoformat()
        return data


class CustomerSummary(FirestoreModel):
    """Lightweight customer summary for listings."""
    customer_id: str
    salon_id: str
    name: str
    phone: str
    email: Optional[str]
    gender: Gender
    total_visits: int
    total_spent: Decimal
    loyalty_points_balance: int
    membership_status: MembershipStatus
    last_visit: Optional[datetime]
    tags: List[str]


class CustomerSearch(FirestoreModel):
    """Customer search parameters."""
    query: Optional[str] = Field(default=None, description="Search by name or phone")
    tags: Optional[List[str]] = Field(default=None, description="Filter by tags")
    membership_status: Optional[MembershipStatus] = Field(default=None, description="Filter by membership")
    min_visits: Optional[int] = Field(default=None, ge=0, description="Minimum visits")
    max_visits: Optional[int] = Field(default=None, ge=0, description="Maximum visits")
    min_spent: Optional[Decimal] = Field(default=None, ge=0, description="Minimum total spent")
    max_spent: Optional[Decimal] = Field(default=None, ge=0, description="Maximum total spent")
    has_birthday_this_month: bool = Field(default=False, description="Birthday in current month")
    has_anniversary_this_month: bool = Field(default=False, description="Anniversary in current month")
    is_active: Optional[bool] = Field(default=None, description="Filter by active status")


class CustomerLoyaltySummary(FirestoreModel):
    """Customer loyalty program summary."""
    customer_id: str
    name: str
    loyalty_points_balance: int
    loyalty_points_value: Decimal
    loyalty_points_earned: int
    loyalty_points_redeemed: int
    loyalty_points_expired: int
    total_visits: int
    total_spent: Decimal
    average_spending: Decimal
    membership_status: MembershipStatus
    tier: str = Field(default="Bronze", description="Loyalty tier based on spending")
    
    @property
    def next_tier_progress(self) -> float:
        """Progress towards next loyalty tier."""
        tier_thresholds = {
            "Bronze": Decimal("0"),
            "Silver": Decimal("10000"),
            "Gold": Decimal("25000"),
            "Platinum": Decimal("50000"),
        }
        current_threshold = tier_thresholds.get(self.tier, Decimal("0"))
        next_tiers = [t for t, v in tier_thresholds.items() if v > current_threshold]
        if not next_tiers:
            return 100.0
        next_threshold = tier_thresholds[next_tiers[0]]
        progress = float((self.total_spent - current_threshold) / (next_threshold - current_threshold) * 100)
        return min(100.0, max(0.0, progress))
