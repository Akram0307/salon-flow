"""Loyalty Program Schemas"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class LoyaltyTier(str, Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"


class LoyaltyTransactionType(str, Enum):
    EARN = "earn"
    REDEEM = "redeem"
    BONUS = "bonus"
    EXPIRE = "expire"
    ADJUSTMENT = "adjustment"


class LoyaltyConfigBase(BaseModel):
    """Base loyalty configuration schema"""
    points_per_rupee: int = Field(default=1, ge=0, description="Points earned per ₹10 spent")
    redemption_rate: Decimal = Field(default=Decimal("1.00"), description="₹ value per point")
    min_points_for_redemption: int = Field(default=100, ge=0)
    max_points_per_transaction: int = Field(default=500, ge=0)
    points_expiry_months: int = Field(default=12, ge=1)
    tier_thresholds: dict = Field(
        default={"bronze": 0, "silver": 500, "gold": 1500, "platinum": 3000}
    )
    tier_benefits: dict = Field(
        default={
            "bronze": {"discount": 0, "bonus_rate": 1.0},
            "silver": {"discount": 5, "bonus_rate": 1.1},
            "gold": {"discount": 10, "bonus_rate": 1.25},
            "platinum": {"discount": 15, "bonus_rate": 1.5}
        }
    )


class LoyaltyConfigResponse(LoyaltyConfigBase):
    """Schema for loyalty configuration response"""
    id: str
    salon_id: str
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LoyaltyAccountBase(BaseModel):
    """Base loyalty account schema"""
    customer_id: str
    total_points: int = 0
    available_points: int = 0
    lifetime_points: int = 0
    current_tier: LoyaltyTier = LoyaltyTier.BRONZE


class LoyaltyAccountResponse(LoyaltyAccountBase):
    """Schema for loyalty account response"""
    id: str
    salon_id: str
    next_tier_threshold: Optional[int] = None
    points_to_next_tier: Optional[int] = None
    tier_benefits: dict = {}
    last_activity_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PointsEarnRequest(BaseModel):
    """Schema for earning points"""
    customer_id: str
    amount: Decimal = Field(..., ge=0, description="Transaction amount in ₹")
    booking_id: Optional[str] = None
    description: Optional[str] = None


class PointsRedeemRequest(BaseModel):
    """Schema for redeeming points"""
    customer_id: str
    points: int = Field(..., gt=0)
    booking_id: Optional[str] = None
    description: Optional[str] = None


class LoyaltyTransactionBase(BaseModel):
    """Base loyalty transaction schema"""
    customer_id: str
    transaction_type: LoyaltyTransactionType
    points: int
    balance_after: int
    description: Optional[str] = None
    reference_type: Optional[str] = None
    reference_id: Optional[str] = None


class LoyaltyTransactionResponse(LoyaltyTransactionBase):
    """Schema for loyalty transaction response"""
    id: str
    salon_id: str
    expires_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class RewardBase(BaseModel):
    """Base reward schema"""
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    points_cost: int = Field(..., gt=0)
    reward_type: str = Field(default="discount", description="discount, free_service, product")
    reward_value: Decimal = Field(..., ge=0)
    is_active: bool = True
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None


class RewardCreate(RewardBase):
    """Schema for creating a reward"""
    salon_id: Optional[str] = None


class RewardResponse(RewardBase):
    """Schema for reward response"""
    id: str
    salon_id: str
    times_redeemed: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class LoyaltySummary(BaseModel):
    """Schema for loyalty summary"""
    total_members: int
    active_members: int
    total_points_issued: int
    total_points_redeemed: int
    tier_distribution: dict
    top_members: List[dict]


class LoyaltyTransactionUpdate(BaseModel):
    """Schema for updating a loyalty transaction"""
    description: Optional[str] = None
    expires_at: Optional[datetime] = None


class LoyaltyTransaction(LoyaltyTransactionBase):
    """Full loyalty transaction schema"""
    id: str
    salon_id: str
    expires_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class LoyaltyTransactionSummary(BaseModel):
    """Schema for loyalty transaction summary"""
    total_transactions: int
    total_points_earned: int
    total_points_redeemed: int
    total_points_expired: int
    transactions_by_type: dict


# Additional classes for compatibility

class LoyaltyTierConfig(BaseModel):
    """Schema for tier configuration"""
    tier: LoyaltyTier
    threshold: int
    discount: Decimal = Decimal("0")
    bonus_rate: Decimal = Decimal("1.0")


class LoyaltyConfig(LoyaltyConfigBase):
    """Full loyalty configuration schema"""
    id: str
    salon_id: str
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LoyaltyTransactionCreate(BaseModel):
    """Schema for creating a loyalty transaction"""
    customer_id: str
    transaction_type: LoyaltyTransactionType
    points: int
    balance_after: Optional[int] = None
    description: Optional[str] = None
    reference_type: Optional[str] = None
    reference_id: Optional[str] = None
    salon_id: Optional[str] = None



class LoyaltyPointsBatch(BaseModel):
    """Schema for batch points operation"""
    customer_ids: List[str]
    points: int
    transaction_type: LoyaltyTransactionType
    description: Optional[str] = None


class LoyaltyAccount(LoyaltyAccountBase):
    """Full loyalty account schema"""
    id: str
    salon_id: str
    next_tier_threshold: Optional[int] = None
    points_to_next_tier: Optional[int] = None
    tier_benefits: dict = {}
    last_activity_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LoyaltyStats(BaseModel):
    """Schema for loyalty statistics"""
    total_members: int
    active_members: int
    total_points_issued: int
    total_points_redeemed: int
    total_points_expired: int
    tier_distribution: dict
    average_points_per_member: Decimal
