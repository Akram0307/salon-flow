"""
Salon Flow SaaS - Pydantic Schemas Package.

This package contains all Pydantic v2 schemas for the salon management system.
Each module handles a specific domain entity with comprehensive validation.
"""

# Base classes and enums
from .base import (
    PaginatedResponse,
    ResourceStatus,
    StaffStatus,
    # Base classes
    FirestoreModel,
    TimestampMixin,
    
    # Enums
    SubscriptionPlan,
    SubscriptionStatus,
    ServiceCategory,
    ResourceType,
    BookingStatus,
    BookingChannel,
    PaymentMethod,
    PaymentStatus,
    MembershipPlanType,
    MembershipStatus,
    LoyaltyTransactionType,
    LoyaltyReferenceType,
    StaffRole,
    Gender,
    ExpertiseLevel,
    SalaryType,
    LeaveType,
    LeaveStatus,
    
    # Constants
    BusinessConstants,
    
    # Utility functions
    generate_entity_id,
    is_late_arrival,
)

# Salon schemas
from .salon import (
    SalonSubscription,
    DayHours,
    OperatingHours,
    SalonLayout,
    SalonBase,
    SalonCreate,
    SalonUpdate,
    Salon,
    SalonSummary,
    SalonSettings,
)

# Customer schemas
from .customer import (
    CustomerPreferences,
    CustomerAddress,
    CustomerBase,
    CustomerCreate,
    CustomerUpdate,
    Customer,
    CustomerSummary,
    CustomerSearch,
    CustomerLoyaltySummary,
)

# Staff schemas
from .staff import (
    StaffSearch,
    StaffSkill,
    ServiceSkill,
    StaffSkills,
    ShiftPreference,
    StaffAvailability,
    CommissionConfig,
    StaffBase,
    StaffCreate,
    StaffUpdate,
    Staff,
    StaffSummary,
    StaffSchedule,
)

# Service schemas
from .service import (
    ServicePricing,
    ServiceDuration,
    ResourceRequirement,
    ServiceBase,
    ServiceCreate,
    ServiceUpdate,
    Service,
    ServiceSummary,
    ServiceCategoryGroup,
    ServiceAvailability,
)

# Booking schemas
from .booking import (
    TimeSlot,
    BookingTimeSlot,
    BookingServiceDetails,
    BookingStaffDetails,
    BookingCustomerDetails,
    BookingResourceDetails,
    BookingBase,
    BookingCreate,
    BookingUpdate,
    BookingStatusUpdate,
    Booking,
    BookingSummary,
    BookingCalendarEvent,
    BookingSearch,
    BookingStats,
)

# Payment schemas
from .payment import (
    InvoiceDetails,
    InvoiceLineItem,
    PaymentBreakdown,
    PaymentSplit,
    PaymentBase,
    PaymentCreate,
    PaymentUpdate,
    Payment,
    PaymentSummary,
    PaymentSearch,
    PaymentStats,
    DailyRevenue,
)

# Membership schemas
from .membership import (
    MembershipType,
    MembershipPlanBenefits,
    MembershipPlanPricing,
    MembershipPlan,
    MembershipUsage,
    MembershipBase,
    MembershipCreate,
    MembershipUpdate,
    MembershipRenewal,
    Membership,
    MembershipSummary,
    MembershipStats,
)

# Loyalty schemas
from .loyalty import (
    LoyaltyTransactionUpdate,
    LoyaltyTier,
    LoyaltyTierConfig,
    LoyaltyConfig,
    LoyaltyTransactionBase,
    LoyaltyTransactionCreate,
    LoyaltyTransaction,
    LoyaltyTransactionSummary,
    LoyaltyPointsBatch,
    LoyaltyAccount,
    LoyaltyStats,
)

# Resource schemas
from .resource import (
    ResourceCapacity,
    ResourceAvailabilitySlot,
    ResourceMaintenance,
    ResourceBase,
    ResourceCreate,
    ResourceUpdate,
    Resource,
    ResourceSummary,
    SalonLayoutZone,
    SalonLayoutConfig,
    ResourceAllocation,
    ResourceUtilizationReport,
)

# Shift schemas
from .shift import (
    LeaveRequestStatus,
    LeaveRequestCreate,
    LeaveRequestUpdate,
    ShiftType,
    ShiftStatus,
    ShiftTemplate,
    ShiftBase,
    ShiftCreate,
    ShiftUpdate,
    Shift,
    ShiftSummary,
    LeaveBalance,
    LeaveRequest,
    StaffWeeklySchedule,
    ScheduleSummary,
)

__all__ = [
    # Base
    "FirestoreModel",
    "TimestampMixin",
    "SubscriptionPlan",
    "SubscriptionStatus",
    "ServiceCategory",
    "ResourceType",
    "BookingStatus",
    "BookingChannel",
    "PaymentMethod",
    "PaymentStatus",
    "MembershipPlanType",
    "MembershipStatus",
    "LoyaltyTransactionType",
    "LoyaltyReferenceType",
    "StaffRole",
    "Gender",
    "ExpertiseLevel",
    "SalaryType",
    "StaffStatus",
    "LeaveType",
    "LeaveStatus",
    "BusinessConstants",
    "generate_entity_id",
    "is_late_arrival",
    "PaginatedResponse",
    
    # Salon
    "DayHours",
    "OperatingHours",
    "SalonLayout",
    "SalonBase",
    "SalonCreate",
    "SalonUpdate",
    "Salon",
    "SalonSummary",
    "SalonSettings",
    "SalonSubscription",
    
    # Customer
    "CustomerPreferences",
    "CustomerAddress",
    "CustomerBase",
    "CustomerCreate",
    "CustomerUpdate",
    "Customer",
    "CustomerSummary",
    "CustomerSearch",
    "CustomerLoyaltySummary",
    
    # Staff
    "ServiceSkill",
    "StaffSkills",
    "ShiftPreference",
    "StaffAvailability",
    "CommissionConfig",
    "StaffBase",
    "StaffCreate",
    "StaffUpdate",
    "Staff",
    "StaffSummary",
    "StaffSchedule",
    "StaffSearch",
    "StaffSkill",
    
    # Service
    "ServicePricing",
    "ServiceDuration",
    "ResourceRequirement",
    "ServiceBase",
    "ServiceCreate",
    "ServiceUpdate",
    "Service",
    "ServiceSummary",
    "ServiceCategoryGroup",
    "ServiceAvailability",
    
    # Booking
    "TimeSlot",
    "BookingTimeSlot",
    "BookingServiceDetails",
    "BookingStaffDetails",
    "BookingCustomerDetails",
    "BookingResourceDetails",
    "BookingBase",
    "BookingCreate",
    "BookingUpdate",
    "BookingStatusUpdate",
    "Booking",
    "BookingSummary",
    "BookingCalendarEvent",
    "BookingSearch",
    "BookingStats",
    
    # Payment
    "InvoiceDetails",
    "InvoiceLineItem",
    "PaymentBreakdown",
    "PaymentSplit",
    "PaymentBase",
    "PaymentCreate",
    "PaymentUpdate",
    "Payment",
    "PaymentSummary",
    "PaymentSearch",
    "PaymentStats",
    "DailyRevenue",
    
    # Membership
    "MembershipPlanBenefits",
    "MembershipPlanPricing",
    "MembershipPlan",
    "MembershipUsage",
    "MembershipBase",
    "MembershipCreate",
    "MembershipUpdate",
    "MembershipRenewal",
    "Membership",
    "MembershipSummary",
    "MembershipStats",
    "MembershipType",
    
    # Loyalty
    "LoyaltyTier",
    "LoyaltyTierConfig",
    "LoyaltyConfig",
    "LoyaltyTransactionBase",
    "LoyaltyTransactionCreate",
    "LoyaltyTransaction",
    "LoyaltyTransactionSummary",
    "LoyaltyPointsBatch",
    "LoyaltyAccount",
    "LoyaltyStats",
    "LoyaltyTransactionUpdate",
    
    # Resource
    "ResourceCapacity",
    "ResourceAvailabilitySlot",
    "ResourceMaintenance",
    "ResourceBase",
    "ResourceCreate",
    "ResourceUpdate",
    "Resource",
    "ResourceSummary",
    "SalonLayoutZone",
    "SalonLayoutConfig",
    "ResourceAllocation",
    "ResourceUtilizationReport",
    "ResourceStatus",
    
    # Shift
    "ShiftType",
    "ShiftStatus",
    "ShiftTemplate",
    "ShiftBase",
    "ShiftCreate",
    "ShiftUpdate",
    "Shift",
    "ShiftSummary",
    "LeaveBalance",
    "LeaveRequest",
    "StaffWeeklySchedule",
    "ScheduleSummary",
    "LeaveRequestStatus",
    "LeaveRequestCreate",
    "LeaveRequestUpdate",
]
