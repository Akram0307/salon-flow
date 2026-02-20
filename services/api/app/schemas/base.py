"""
Base schemas and enums for Salon Flow SaaS.
Contains common enums, base models, and utility functions.
"""
from datetime import datetime, date, time, timedelta
from decimal import Decimal
from enum import Enum
from typing import Optional, List, Dict, Any, Generic, TypeVar
from uuid import uuid4

from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator


# ============================================================================
# ENUMS
# ============================================================================

class SubscriptionPlan(str, Enum):
    """Salon subscription plan types."""
    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, Enum):
    """Salon subscription status."""
    TRIAL = "trial"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class StaffRole(str, Enum):
    """Staff member roles in salon."""
    OWNER = "owner"
    MANAGER = "manager"
    RECEPTIONIST = "receptionist"
    STYLIST = "stylist"
    ASSISTANT = "assistant"
    CUSTOMER = "customer"


class ExpertiseLevel(str, Enum):
    """Staff expertise level for services."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    EXPERT = "expert"


class SalaryType(str, Enum):
    """Staff salary payment type."""
    FIXED = "fixed"
    COMMISSION = "commission"
    HYBRID = "hybrid"


class ServiceCategory(str, Enum):
    """Service category types."""
    HAIRCUT = "haircut"
    HAIR_COLOR = "hair_color"
    HAIR_TREATMENT = "hair_treatment"
    FACIAL = "facial"
    SKIN_TREATMENT = "skin_treatment"
    BRIDAL = "bridal"
    SPA = "spa"
    MANICURE = "manicure"
    PEDICURE = "pedicure"
    WAXING = "waxing"
    THREADING = "threading"
    MAKEUP = "makeup"
    OTHER = "other"


class ResourceType(str, Enum):
    """Resource types for salon layout."""
    CHAIR_MENS = "chair_mens"
    CHAIR_WOMENS = "chair_womens"
    ROOM_BRIDAL = "room_bridal"
    ROOM_TREATMENT = "room_treatment"
    ROOM_SPA = "room_spa"
    ANY = "any"


class BookingStatus(str, Enum):
    """Booking status lifecycle."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CHECKED_IN = "checked_in"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class BookingChannel(str, Enum):
    """Channel through which booking was made."""
    WALK_IN = "walk_in"
    PHONE = "phone"
    ONLINE = "online"
    WHATSAPP = "whatsapp"


class PaymentMethod(str, Enum):
    """Payment method types."""
    CASH = "cash"
    UPI = "upi"
    CARD = "card"
    WALLET = "wallet"
    MEMBERSHIP = "membership"


class PaymentStatus(str, Enum):
    """Payment status."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class MembershipPlanType(str, Enum):
    """Membership plan duration types."""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"


class MembershipStatus(str, Enum):
    """Membership status."""
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    PENDING = "pending"


class LoyaltyTransactionType(str, Enum):
    """Type of loyalty transaction."""
    EARN = "earn"
    REDEEM = "redeem"
    EXPIRE = "expire"
    BONUS = "bonus"


class LoyaltyReferenceType(str, Enum):
    """Reference type for loyalty transaction."""
    BOOKING = "booking"
    REFERRAL = "referral"
    PROMOTION = "promotion"
    MANUAL = "manual"


class LeaveType(str, Enum):
    """Type of leave for staff."""
    SICK = "sick"
    CASUAL = "casual"
    EARNED = "earned"
    UNPAID = "unpaid"


class LeaveStatus(str, Enum):
    """Leave request status."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Gender(str, Enum):
    """Gender options."""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


# ============================================================================
# BUSINESS CONSTANTS
# ============================================================================

class BusinessConstants:
    """Business rules and constants for Salon Flow."""
    GST_RATE: Decimal = Decimal("0.05")  # 5% GST
    GST_RATE_PERCENTAGE: int = 5
    
    # Loyalty Program
    LOYALTY_POINTS_PER_RUPEE: int = 10  # 1 point per ₹10 spent
    LOYALTY_POINT_VALUE_PAISA: int = 100  # 1 point = ₹1 (100 paisa)
    LOYALTY_EXPIRY_MONTHS: int = 12
    
    # Membership
    MEMBERSHIP_RENEWAL_DAYS_BEFORE: int = 15
    
    # Booking
    LATE_ARRIVAL_GRACE_MINUTES: int = 15
    BOOKING_BUFFER_MINUTES: int = 15
    
    # Default salon layout
    DEFAULT_MENS_CHAIRS: int = 6
    DEFAULT_WOMENS_CHAIRS: int = 4
    DEFAULT_SERVICE_ROOMS: int = 4


# ============================================================================
# BASE MODELS
# ============================================================================

class TimestampMixin(BaseModel):
    """Mixin for created_at and updated_at timestamps."""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()


class FirestoreModel(BaseModel):
    """Base model with Firestore serialization helpers."""
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        use_enum_values=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            time: lambda v: v.isoformat(),
            Decimal: lambda v: float(v),
        }
    )
    
    def to_firestore(self) -> Dict[str, Any]:
        """Convert model to Firestore-compatible dictionary.
        
        Firestore requires:
        - Enums as strings
        - Datetimes as ISO strings or Timestamps
        - Decimals as floats
        - None values should be omitted or explicitly set
        
        Returns:
            Dict[str, Any]: Firestore-compatible dictionary
        """
        data = self.model_dump(mode='json', exclude_none=True)
        return data
    
    @classmethod
    def from_firestore(cls, data: Dict[str, Any]) -> 'FirestoreModel':
        """Create model from Firestore document data.
        
        Args:
            data: Dictionary from Firestore document
            
        Returns:
            Instance of the model
        """
        return cls.model_validate(data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to regular dictionary (alias for model_dump)."""
        return self.model_dump(mode='python')
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return self.model_dump_json()


class EntityBase(FirestoreModel, TimestampMixin):
    """Base entity with common fields for all salon entities."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    salon_id: str = Field(..., description="Reference to the salon/tenant")
    
    @field_validator('id', mode='before')
    @classmethod
    def generate_id_if_empty(cls, v: Optional[str]) -> str:
        if not v:
            return str(uuid4())
        return v


class PaginatedResponse(BaseModel, Generic[TypeVar('T')]):
    """Generic paginated response wrapper."""
    items: List[Any] = Field(default_factory=list)
    total: int = Field(default=0)
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    total_pages: int = Field(default=0)
    has_next: bool = Field(default=False)
    has_previous: bool = Field(default=False)
    
    @model_validator(mode='after')
    def calculate_pagination(self) -> 'PaginatedResponse':
        if self.total > 0 and self.page_size > 0:
            self.total_pages = (self.total + self.page_size - 1) // self.page_size
            self.has_next = self.page < self.total_pages
            self.has_previous = self.page > 1
        return self


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def generate_entity_id(prefix: str = "") -> str:
    """Generate a unique entity ID with optional prefix.
    
    Args:
        prefix: Optional prefix for the ID (e.g., 'salon', 'cust')
        
    Returns:
        Unique identifier string
    """
    unique_id = str(uuid4()).replace('-', '')[:12]
    return f"{prefix}_{unique_id}" if prefix else unique_id


def calculate_gst(amount: Decimal, rate: Decimal = BusinessConstants.GST_RATE) -> Decimal:
    """Calculate GST amount for a given base amount.
    
    Args:
        amount: Base amount before GST
        rate: GST rate (default 5%)
        
    Returns:
        GST amount
    """
    return (amount * rate).quantize(Decimal('0.01'))


def calculate_total_with_gst(amount: Decimal, rate: Decimal = BusinessConstants.GST_RATE) -> Decimal:
    """Calculate total amount including GST.
    
    Args:
        amount: Base amount before GST
        rate: GST rate (default 5%)
        
    Returns:
        Total amount including GST
    """
    return (amount * (1 + rate)).quantize(Decimal('0.01'))


def calculate_loyalty_points(amount: Decimal) -> int:
    """Calculate loyalty points for a given amount.
    
    Args:
        amount: Amount spent in rupees
        
    Returns:
        Number of loyalty points earned
    """
    return int(amount // BusinessConstants.LOYALTY_POINTS_PER_RUPEE)


def get_loyalty_expiry_date(from_date: date = None) -> date:
    """Calculate loyalty points expiry date.
    
    Args:
        from_date: Starting date (defaults to today)
        
    Returns:
        Expiry date (12 months from start)
    """
    start = from_date or date.today()
    return date(start.year, start.month, start.day) + timedelta(days=365)


def is_late_arrival(booking_time: time, arrival_time: time, grace_minutes: int = None) -> tuple[bool, int]:
    """Check if arrival is late and by how many minutes.
    
    Args:
        booking_time: Scheduled booking time
        arrival_time: Actual arrival time
        grace_minutes: Grace period in minutes
        
    Returns:
        Tuple of (is_late, minutes_late)
    """
    grace = grace_minutes or BusinessConstants.LATE_ARRIVAL_GRACE_MINUTES
    
    # Convert times to minutes for comparison
    booking_minutes = booking_time.hour * 60 + booking_time.minute
    arrival_minutes = arrival_time.hour * 60 + arrival_time.minute
    
    minutes_late = arrival_minutes - booking_minutes
    is_late = minutes_late > grace
    
    return is_late, max(0, minutes_late)


class StaffStatus(str, Enum):
    """Staff member status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ON_LEAVE = "on_leave"
    TERMINATED = "terminated"


class ResourceStatus(str, Enum):
    """Resource status enumeration."""
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    MAINTENANCE = "maintenance"
    BLOCKED = "blocked"


