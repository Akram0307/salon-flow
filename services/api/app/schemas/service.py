"""
Service schemas for Salon Flow SaaS.
Handles service definitions, pricing, and resource requirements.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, List, Any

from pydantic import Field, field_validator, model_validator

from .base import (
    FirestoreModel,
    TimestampMixin,
    ServiceCategory,
    ResourceType,
    BusinessConstants,
    generate_entity_id,
)


# ============================================================================
# SERVICE PRICING
# ============================================================================

class ServicePricing(FirestoreModel):
    """Service pricing configuration."""
    base_price: Decimal = Field(..., ge=0, description="Base price in rupees")
    min_price: Optional[Decimal] = Field(default=None, ge=0, description="Minimum price for variable pricing")
    max_price: Optional[Decimal] = Field(default=None, ge=0, description="Maximum price for variable pricing")
    is_variable_pricing: bool = Field(default=False, description="Whether price varies")
    
    # Staff-based pricing
    junior_price: Optional[Decimal] = Field(default=None, ge=0, description="Price for junior stylist")
    senior_price: Optional[Decimal] = Field(default=None, ge=0, description="Price for senior stylist")
    expert_price: Optional[Decimal] = Field(default=None, ge=0, description="Price for expert stylist")
    
    # Time-based pricing
    peak_hours_surcharge: Decimal = Field(default=Decimal("0"), ge=0, le=1, description="Surcharge during peak hours")
    weekend_surcharge: Decimal = Field(default=Decimal("0"), ge=0, le=1, description="Surcharge on weekends")
    
    # Membership pricing
    member_discount_percent: Decimal = Field(default=Decimal("0"), ge=0, le=1, description="Discount for members")
    
    @model_validator(mode='after')
    def validate_pricing(self) -> 'ServicePricing':
        if self.is_variable_pricing:
            if self.min_price is not None and self.max_price is not None:
                if self.min_price > self.max_price:
                    raise ValueError("Min price cannot be greater than max price")
        return self
    
    def get_price_for_staff_level(self, level: str) -> Decimal:
        """Get price based on staff expertise level."""
        level_prices = {
            'beginner': self.junior_price or self.base_price,
            'intermediate': self.senior_price or self.base_price,
            'expert': self.expert_price or self.base_price,
        }
        return level_prices.get(level, self.base_price)
    
    def to_firestore(self) -> Dict[str, Any]:
        data = super().to_firestore()
        for key in ['base_price', 'min_price', 'max_price', 'junior_price', 'senior_price', 'expert_price',
                    'peak_hours_surcharge', 'weekend_surcharge', 'member_discount_percent']:
            if key in data and data[key] is not None:
                data[key] = float(data[key])
        return data


class ServiceDuration(FirestoreModel):
    """Service duration configuration."""
    base_minutes: int = Field(..., ge=5, le=480, description="Base duration in minutes")
    min_minutes: Optional[int] = Field(default=None, ge=5, description="Minimum duration")
    max_minutes: Optional[int] = Field(default=None, le=480, description="Maximum duration")
    buffer_before: int = Field(default=0, ge=0, le=30, description="Buffer time before service")
    buffer_after: int = Field(default=0, ge=0, le=30, description="Buffer time after service")
    
    @property
    def total_minutes(self) -> int:
        """Total time including buffers."""
        return self.base_minutes + self.buffer_before + self.buffer_after
    
    @model_validator(mode='after')
    def validate_duration(self) -> 'ServiceDuration':
        if self.min_minutes and self.max_minutes:
            if self.min_minutes > self.max_minutes:
                raise ValueError("Min duration cannot be greater than max duration")
        return self


# ============================================================================
# SERVICE RESOURCE CONFIG
# ============================================================================

class ResourceRequirement(FirestoreModel):
    """Resource requirements for a service."""
    resource_type: ResourceType = Field(..., description="Type of resource needed")
    is_exclusive: bool = Field(
        default=False,
        description="Whether resource is exclusively used (e.g., bridal room)"
    )
    resource_priority: List[ResourceType] = Field(
        default_factory=list,
        description="Priority order of acceptable resources"
    )
    requires_specific_resource: bool = Field(
        default=False,
        description="Whether specific resource ID is required"
    )
    specific_resource_ids: List[str] = Field(
        default_factory=list,
        description="Specific resource IDs if required"
    )
    
    @model_validator(mode='after')
    def set_defaults(self) -> 'ResourceRequirement':
        # Set default priority if not specified
        if not self.resource_priority:
            self.resource_priority = [self.resource_type]
        return self


# ============================================================================
# SERVICE SCHEMAS
# ============================================================================

class ServiceBase(FirestoreModel, TimestampMixin):
    """Base service schema with common fields."""
    salon_id: str = Field(..., description="Reference to the salon")
    name: str = Field(..., min_length=2, max_length=100, description="Service name")
    description: Optional[str] = Field(default=None, max_length=500, description="Service description")
    category: ServiceCategory = Field(..., description="Service category")
    
    # Pricing
    pricing: ServicePricing = Field(..., description="Pricing configuration")
    duration: ServiceDuration = Field(..., description="Duration configuration")
    
    # Resource requirements
    resource_requirement: ResourceRequirement = Field(
        default_factory=lambda: ResourceRequirement(resource_type=ResourceType.ANY),
        description="Resource requirements"
    )
    
    # Tax
    gst_rate: Decimal = Field(
        default=BusinessConstants.GST_RATE,
        ge=0,
        le=0.28,
        description="GST rate (default 5%)"
    )
    hsn_code: Optional[str] = Field(default=None, max_length=10, description="HSN/SAC code")
    
    # Status
    is_active: bool = Field(default=True, description="Whether service is active")
    is_popular: bool = Field(default=False, description="Mark as popular/trending")
    is_featured: bool = Field(default=False, description="Featured on booking page")
    
    # Display
    display_order: int = Field(default=0, ge=0, description="Order for display")
    image_url: Optional[str] = Field(default=None, max_length=500, description="Service image URL")
    
    # Gender preference
    gender_preference: Optional[str] = Field(
        default=None,
        description="Preferred gender: male, female, or null for all"
    )
    
    # Booking settings
    requires_consultation: bool = Field(default=False, description="Requires prior consultation")
    max_advance_booking_days: Optional[int] = Field(default=None, ge=1, le=90, description="Max days in advance")
    min_advance_booking_hours: int = Field(default=0, ge=0, le=72, description="Min hours in advance")
    
    @property
    def price_with_gst(self) -> Decimal:
        """Calculate price including GST."""
        return (self.pricing.base_price * (1 + self.gst_rate)).quantize(Decimal('0.01'))
    
    @property
    def gst_amount(self) -> Decimal:
        """Calculate GST amount."""
        return (self.pricing.base_price * self.gst_rate).quantize(Decimal('0.01'))
    
    @property
    def total_duration_minutes(self) -> int:
        """Get total duration including buffers."""
        return self.duration.total_minutes


class ServiceCreate(ServiceBase):
    """Schema for creating a new service."""
    salon_id: str = Field(default="", description="Reference to the salon (injected from auth)")
    service_id: str = Field(default_factory=lambda: generate_entity_id("svc"))
    
    # Staff assignment
    eligible_staff_ids: List[str] = Field(
        default_factory=list,
        description="Staff IDs who can perform this service"
    )
    
    # Complementary services
    complementary_service_ids: List[str] = Field(
        default_factory=list,
        description="Services that go well with this one"
    )
    addon_service_ids: List[str] = Field(
        default_factory=list,
        description="Add-on services available"
    )


class ServiceUpdate(FirestoreModel):
    """Schema for updating service information."""
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    category: Optional[ServiceCategory] = Field(default=None)
    pricing: Optional[ServicePricing] = Field(default=None)
    duration: Optional[ServiceDuration] = Field(default=None)
    resource_requirement: Optional[ResourceRequirement] = Field(default=None)
    gst_rate: Optional[Decimal] = Field(default=None, ge=0, le=0.28)
    hsn_code: Optional[str] = Field(default=None, max_length=10)
    is_active: Optional[bool] = Field(default=None)
    is_popular: Optional[bool] = Field(default=None)
    is_featured: Optional[bool] = Field(default=None)
    display_order: Optional[int] = Field(default=None, ge=0)
    image_url: Optional[str] = Field(default=None, max_length=500)
    gender_preference: Optional[str] = Field(default=None)
    requires_consultation: Optional[bool] = Field(default=None)
    max_advance_booking_days: Optional[int] = Field(default=None, ge=1, le=90)
    min_advance_booking_hours: Optional[int] = Field(default=None, ge=0, le=72)
    eligible_staff_ids: Optional[List[str]] = Field(default=None)
    complementary_service_ids: Optional[List[str]] = Field(default=None)
    addon_service_ids: Optional[List[str]] = Field(default=None)


class Service(ServiceBase):
    """Complete service entity with all fields."""
    service_id: str = Field(..., description="Unique service identifier")
    
    # Staff assignment
    eligible_staff_ids: List[str] = Field(default_factory=list)
    
    # Related services
    complementary_service_ids: List[str] = Field(default_factory=list)
    addon_service_ids: List[str] = Field(default_factory=list)
    parent_service_id: Optional[str] = Field(default=None, description="Parent service if this is a variant")
    
    # Statistics
    total_bookings: int = Field(default=0, ge=0, description="Total times booked")
    total_revenue: Decimal = Field(default=Decimal("0"), ge=0, description="Total revenue generated")
    average_rating: Decimal = Field(default=Decimal("0"), ge=0, le=5, description="Average customer rating")
    total_reviews: int = Field(default=0, ge=0, description="Total reviews received")
    
    # Loyalty
    loyalty_points: int = Field(default=0, ge=0, description="Loyalty points earned for this service")
    
    def calculate_loyalty_points(self) -> int:
        """Calculate loyalty points for this service."""
        return int(self.pricing.base_price // BusinessConstants.LOYALTY_POINTS_PER_RUPEE)
    
    def get_price_for_time(self, is_weekend: bool = False, is_peak: bool = False) -> Decimal:
        """Get price adjusted for time-based surcharges."""
        price = self.pricing.base_price
        if is_weekend and self.pricing.weekend_surcharge > 0:
            price = price * (1 + self.pricing.weekend_surcharge)
        if is_peak and self.pricing.peak_hours_surcharge > 0:
            price = price * (1 + self.pricing.peak_hours_surcharge)
        return price.quantize(Decimal('0.01'))
    
    def get_member_price(self) -> Decimal:
        """Get price for members."""
        if self.pricing.member_discount_percent > 0:
            return (self.pricing.base_price * (1 - self.pricing.member_discount_percent)).quantize(Decimal('0.01'))
        return self.pricing.base_price
    
    def to_firestore(self) -> Dict[str, Any]:
        """Convert to Firestore-compatible dictionary."""
        data = super().to_firestore()
        data['pricing'] = self.pricing.to_firestore()
        data['duration'] = self.duration.to_firestore()
        data['resource_requirement'] = self.resource_requirement.to_firestore()
        data['gst_rate'] = float(self.gst_rate)
        data['total_revenue'] = float(self.total_revenue)
        data['average_rating'] = float(self.average_rating)
        return data


class ServiceSummary(FirestoreModel):
    """Lightweight service summary for listings."""
    service_id: str
    salon_id: str
    name: str
    category: ServiceCategory
    base_price: Decimal
    duration_minutes: int
    resource_type: ResourceType
    is_active: bool
    is_popular: bool
    image_url: Optional[str]
    average_rating: Decimal


class ServiceCategoryGroup(FirestoreModel):
    """Group of services by category."""
    category: ServiceCategory
    category_name: str
    services: List[ServiceSummary]
    total_services: int
    
    @property
    def min_price(self) -> Decimal:
        """Get minimum price in category."""
        if not self.services:
            return Decimal("0")
        return min(s.base_price for s in self.services)
    
    @property
    def max_price(self) -> Decimal:
        """Get maximum price in category."""
        if not self.services:
            return Decimal("0")
        return max(s.base_price for s in self.services)


class ServiceAvailability(FirestoreModel):
    """Service availability for a specific time slot."""
    service_id: str
    service_name: str
    date: str  # ISO date string
    time_slot: str  # HH:MM format
    available_staff: List[str] = Field(default_factory=list)
    available_resources: List[str] = Field(default_factory=list)
    is_available: bool = True
    available_slots: int = 0
    total_slots: int = 0
    
    @property
    def utilization_percent(self) -> float:
        """Calculate slot utilization."""
        if self.total_slots == 0:
            return 0.0
        return ((self.total_slots - self.available_slots) / self.total_slots) * 100
