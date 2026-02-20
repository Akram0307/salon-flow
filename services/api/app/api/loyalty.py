"""Loyalty Program API Router"""
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.api.dependencies import get_current_user, require_role, get_salon_id
from app.schemas.loyalty import (
    LoyaltyConfigResponse, LoyaltyAccountResponse,
    PointsEarnRequest, PointsRedeemRequest, LoyaltyTransactionResponse,
    RewardCreate, RewardResponse, LoyaltySummary,
    LoyaltyTier, LoyaltyTransactionType
)
from app.models.base import FirestoreBase
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/loyalty", tags=["Loyalty"])


class LoyaltyConfig(FirestoreBase):
    """Loyalty configuration model"""
    collection_name = "loyalty_configs"
    id_field = "config_id"
    
    def __init__(self, **data):
        super().__init__(**data)
        self.config_id = data.get("config_id", str(uuid.uuid4()))
        self.salon_id = data.get("salon_id", "")
        self.points_per_rupee = data.get("points_per_rupee", 1)
        self.redemption_rate = Decimal(str(data.get("redemption_rate", "1.00")))
        self.min_points_for_redemption = data.get("min_points_for_redemption", 100)
        self.max_points_per_transaction = data.get("max_points_per_transaction", 500)
        self.points_expiry_months = data.get("points_expiry_months", 12)
        self.tier_thresholds = data.get("tier_thresholds", {"bronze": 0, "silver": 500, "gold": 1500, "platinum": 3000})
        self.tier_benefits = data.get("tier_benefits", {})
        self.is_active = data.get("is_active", True)
        self.created_at = data.get("created_at", datetime.utcnow())
        self.updated_at = data.get("updated_at", datetime.utcnow())
    
    def to_dict(self):
        return {
            "id": self.config_id,
            "salon_id": self.salon_id,
            "points_per_rupee": self.points_per_rupee,
            "redemption_rate": float(self.redemption_rate),
            "min_points_for_redemption": self.min_points_for_redemption,
            "max_points_per_transaction": self.max_points_per_transaction,
            "points_expiry_months": self.points_expiry_months,
            "tier_thresholds": self.tier_thresholds,
            "tier_benefits": self.tier_benefits,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class LoyaltyAccount(FirestoreBase):
    """Loyalty account model"""
    collection_name = "loyalty_accounts"
    id_field = "account_id"
    
    def __init__(self, **data):
        super().__init__(**data)
        self.account_id = data.get("account_id", str(uuid.uuid4()))
        self.customer_id = data.get("customer_id", "")
        self.salon_id = data.get("salon_id", "")
        self.total_points = data.get("total_points", 0)
        self.available_points = data.get("available_points", 0)
        self.lifetime_points = data.get("lifetime_points", 0)
        self.current_tier = data.get("current_tier", LoyaltyTier.BRONZE.value)
        self.last_activity_at = data.get("last_activity_at")
        self.created_at = data.get("created_at", datetime.utcnow())
        self.updated_at = data.get("updated_at", datetime.utcnow())
    
    def update_tier(self, tier_thresholds: dict):
        """Update tier based on lifetime points"""
        if self.lifetime_points >= tier_thresholds.get("platinum", 3000):
            self.current_tier = LoyaltyTier.PLATINUM.value
        elif self.lifetime_points >= tier_thresholds.get("gold", 1500):
            self.current_tier = LoyaltyTier.GOLD.value
        elif self.lifetime_points >= tier_thresholds.get("silver", 500):
            self.current_tier = LoyaltyTier.SILVER.value
        else:
            self.current_tier = LoyaltyTier.BRONZE.value
    
    def to_dict(self):
        return {
            "id": self.account_id,
            "customer_id": self.customer_id,
            "salon_id": self.salon_id,
            "total_points": self.total_points,
            "available_points": self.available_points,
            "lifetime_points": self.lifetime_points,
            "current_tier": self.current_tier,
            "last_activity_at": self.last_activity_at.isoformat() if self.last_activity_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class LoyaltyTransaction(FirestoreBase):
    """Loyalty transaction model"""
    collection_name = "loyalty_transactions"
    id_field = "transaction_id"
    
    def __init__(self, **data):
        super().__init__(**data)
        self.transaction_id = data.get("transaction_id", str(uuid.uuid4()))
        self.customer_id = data.get("customer_id", "")
        self.salon_id = data.get("salon_id", "")
        self.transaction_type = data.get("transaction_type", LoyaltyTransactionType.EARN.value)
        self.points = data.get("points", 0)
        self.balance_after = data.get("balance_after", 0)
        self.description = data.get("description")
        self.reference_type = data.get("reference_type")
        self.reference_id = data.get("reference_id")
        self.expires_at = data.get("expires_at")
        self.created_at = data.get("created_at", datetime.utcnow())
    
    def to_dict(self):
        return {
            "id": self.transaction_id,
            "customer_id": self.customer_id,
            "salon_id": self.salon_id,
            "transaction_type": self.transaction_type,
            "points": self.points,
            "balance_after": self.balance_after,
            "description": self.description,
            "reference_type": self.reference_type,
            "reference_id": self.reference_id,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Reward(FirestoreBase):
    """Reward model"""
    collection_name = "rewards"
    id_field = "reward_id"
    
    def __init__(self, **data):
        super().__init__(**data)
        self.reward_id = data.get("reward_id", str(uuid.uuid4()))
        self.salon_id = data.get("salon_id", "")
        self.name = data.get("name", "")
        self.description = data.get("description")
        self.points_cost = data.get("points_cost", 0)
        self.reward_type = data.get("reward_type", "discount")
        self.reward_value = Decimal(str(data.get("reward_value", 0)))
        self.is_active = data.get("is_active", True)
        self.valid_from = data.get("valid_from")
        self.valid_until = data.get("valid_until")
        self.times_redeemed = data.get("times_redeemed", 0)
        self.created_at = data.get("created_at", datetime.utcnow())
    
    def to_dict(self):
        return {
            "id": self.reward_id,
            "salon_id": self.salon_id,
            "name": self.name,
            "description": self.description,
            "points_cost": self.points_cost,
            "reward_type": self.reward_type,
            "reward_value": float(self.reward_value),
            "is_active": self.is_active,
            "valid_from": self.valid_from.isoformat() if self.valid_from else None,
            "valid_until": self.valid_until.isoformat() if self.valid_until else None,
            "times_redeemed": self.times_redeemed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ==================== Configuration ====================

@router.get("/config", response_model=LoyaltyConfigResponse)
async def get_loyalty_config(
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(get_current_user)
):
    """Get loyalty program configuration"""
    configs = await LoyaltyConfig.find_all(salon_id=salon_id)
    if configs:
        return LoyaltyConfigResponse(**configs[0].to_dict())
    
    # Return default config
    default_config = LoyaltyConfig(salon_id=salon_id)
    return LoyaltyConfigResponse(**default_config.to_dict())


@router.put("/config", response_model=LoyaltyConfigResponse)
async def update_loyalty_config(
    points_per_rupee: int = Query(..., ge=0),
    redemption_rate: Decimal = Query(..., ge=0),
    min_points_for_redemption: int = Query(..., ge=0),
    points_expiry_months: int = Query(..., ge=1),
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(require_role(["owner", "manager"]))
):
    """Update loyalty program configuration"""
    configs = await LoyaltyConfig.find_all(salon_id=salon_id)
    
    if configs:
        config = configs[0]
    else:
        config = LoyaltyConfig(salon_id=salon_id)
    
    config.points_per_rupee = points_per_rupee
    config.redemption_rate = redemption_rate
    config.min_points_for_redemption = min_points_for_redemption
    config.points_expiry_months = points_expiry_months
    config.updated_at = datetime.utcnow()
    await config.save()
    
    return LoyaltyConfigResponse(**config.to_dict())


# ==================== Accounts ====================

@router.get("/accounts", response_model=List[LoyaltyAccountResponse])
async def list_loyalty_accounts(
    tier: Optional[LoyaltyTier] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0),
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(get_current_user)
):
    """List loyalty accounts"""
    filters = {"salon_id": salon_id}
    if tier:
        filters["current_tier"] = tier.value
    
    accounts = await LoyaltyAccount.find_all(**filters, limit=limit, offset=offset)
    return [LoyaltyAccountResponse(**a.to_dict()) for a in accounts]


@router.get("/accounts/{customer_id}", response_model=LoyaltyAccountResponse)
async def get_loyalty_account(
    customer_id: str,
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(get_current_user)
):
    """Get customer's loyalty account"""
    accounts = await LoyaltyAccount.find_all(customer_id=customer_id, salon_id=salon_id)
    
    if not accounts:
        # Create new account
        account = LoyaltyAccount(customer_id=customer_id, salon_id=salon_id)
        await account.save()
        return LoyaltyAccountResponse(**account.to_dict())
    
    return LoyaltyAccountResponse(**accounts[0].to_dict())


# ==================== Points Operations ====================

@router.post("/points/earn", response_model=LoyaltyTransactionResponse, status_code=status.HTTP_201_CREATED)
async def earn_points(
    data: PointsEarnRequest,
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(require_role(["owner", "manager", "receptionist"]))
):
    """Earn loyalty points for a customer"""
    # Get or create account
    accounts = await LoyaltyAccount.find_all(customer_id=data.customer_id, salon_id=salon_id)
    if accounts:
        account = accounts[0]
    else:
        account = LoyaltyAccount(customer_id=data.customer_id, salon_id=salon_id)
    
    # Get config
    configs = await LoyaltyConfig.find_all(salon_id=salon_id)
    config = configs[0] if configs else LoyaltyConfig(salon_id=salon_id)
    
    # Calculate points (1 point per ₹10 spent)
    points = int(data.amount / 10) * config.points_per_rupee
    
    # Apply tier bonus
    tier_benefits = config.tier_benefits.get(account.current_tier, {})
    bonus_rate = tier_benefits.get("bonus_rate", 1.0)
    points = int(points * bonus_rate)
    
    # Update account
    account.total_points += points
    account.available_points += points
    account.lifetime_points += points
    account.update_tier(config.tier_thresholds)
    account.last_activity_at = datetime.utcnow()
    account.updated_at = datetime.utcnow()
    await account.save()
    
    # Create transaction
    transaction = LoyaltyTransaction(
        customer_id=data.customer_id,
        salon_id=salon_id,
        transaction_type=LoyaltyTransactionType.EARN.value,
        points=points,
        balance_after=account.available_points,
        description=data.description or f"Points earned for ₹{data.amount} purchase",
        reference_type="booking",
        reference_id=data.booking_id,
        expires_at=datetime.utcnow() + timedelta(days=config.points_expiry_months * 30)
    )
    await transaction.save()
    
    return LoyaltyTransactionResponse(**transaction.to_dict())


@router.post("/points/redeem", response_model=LoyaltyTransactionResponse)
async def redeem_points(
    data: PointsRedeemRequest,
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(require_role(["owner", "manager", "receptionist"]))
):
    """Redeem loyalty points"""
    accounts = await LoyaltyAccount.find_all(customer_id=data.customer_id, salon_id=salon_id)
    if not accounts:
        raise HTTPException(status_code=404, detail="Loyalty account not found")
    
    account = accounts[0]
    
    # Get config
    configs = await LoyaltyConfig.find_all(salon_id=salon_id)
    config = configs[0] if configs else LoyaltyConfig(salon_id=salon_id)
    
    # Validate redemption
    if data.points < config.min_points_for_redemption:
        raise HTTPException(
            status_code=400,
            detail=f"Minimum {config.min_points_for_redemption} points required for redemption"
        )
    
    if data.points > config.max_points_per_transaction:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum {config.max_points_per_transaction} points can be redeemed per transaction"
        )
    
    if account.available_points < data.points:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient points. Available: {account.available_points}"
        )
    
    # Update account
    account.available_points -= data.points
    account.last_activity_at = datetime.utcnow()
    account.updated_at = datetime.utcnow()
    await account.save()
    
    # Create transaction
    transaction = LoyaltyTransaction(
        customer_id=data.customer_id,
        salon_id=salon_id,
        transaction_type=LoyaltyTransactionType.REDEEM.value,
        points=-data.points,
        balance_after=account.available_points,
        description=data.description or "Points redeemed",
        reference_type="booking",
        reference_id=data.booking_id
    )
    await transaction.save()
    
    return LoyaltyTransactionResponse(**transaction.to_dict())


@router.get("/transactions", response_model=List[LoyaltyTransactionResponse])
async def list_transactions(
    customer_id: Optional[str] = Query(None),
    transaction_type: Optional[LoyaltyTransactionType] = Query(None),
    limit: int = Query(50, le=100),
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(get_current_user)
):
    """List loyalty transactions"""
    filters = {"salon_id": salon_id}
    if customer_id:
        filters["customer_id"] = customer_id
    if transaction_type:
        filters["transaction_type"] = transaction_type.value
    
    transactions = await LoyaltyTransaction.find_all(**filters, limit=limit)
    return [LoyaltyTransactionResponse(**t.to_dict()) for t in transactions]


# ==================== Rewards ====================

@router.post("/rewards", response_model=RewardResponse, status_code=status.HTTP_201_CREATED)
async def create_reward(
    data: RewardCreate,
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(require_role(["owner", "manager"]))
):
    """Create a redeemable reward"""
    reward = Reward(
        salon_id=salon_id,
        name=data.name,
        description=data.description,
        points_cost=data.points_cost,
        reward_type=data.reward_type,
        reward_value=data.reward_value,
        is_active=data.is_active,
        valid_from=data.valid_from,
        valid_until=data.valid_until
    )
    await reward.save()
    return RewardResponse(**reward.to_dict())


@router.get("/rewards", response_model=List[RewardResponse])
async def list_rewards(
    is_active: Optional[bool] = Query(None),
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(get_current_user)
):
    """List available rewards"""
    filters = {"salon_id": salon_id}
    if is_active is not None:
        filters["is_active"] = is_active
    
    rewards = await Reward.find_all(**filters)
    return [RewardResponse(**r.to_dict()) for r in rewards]


@router.delete("/rewards/{reward_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reward(
    reward_id: str,
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(require_role(["owner", "manager"]))
):
    """Delete a reward"""
    reward = await Reward.find_by_id(reward_id, salon_id)
    if not reward:
        raise HTTPException(status_code=404, detail="Reward not found")
    
    reward.is_active = False
    await reward.save()


# ==================== Summary ====================

@router.get("/summary", response_model=LoyaltySummary)
async def get_loyalty_summary(
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(require_role(["owner", "manager"]))
):
    """Get loyalty program summary"""
    accounts = await LoyaltyAccount.find_all(salon_id=salon_id)
    
    total_members = len(accounts)
    active_members = sum(1 for a in accounts if a.last_activity_at and 
                        (datetime.utcnow() - a.last_activity_at).days < 90)
    
    total_points_issued = sum(a.lifetime_points for a in accounts)
    total_points_redeemed = sum(a.lifetime_points - a.available_points for a in accounts)
    
    tier_distribution = {}
    for tier in LoyaltyTier:
        tier_distribution[tier.value] = sum(1 for a in accounts if a.current_tier == tier.value)
    
    top_members = sorted(accounts, key=lambda x: x.lifetime_points, reverse=True)[:10]
    top_members_data = [{"customer_id": a.customer_id, "points": a.lifetime_points, "tier": a.current_tier} 
                        for a in top_members]
    
    return LoyaltySummary(
        total_members=total_members,
        active_members=active_members,
        total_points_issued=total_points_issued,
        total_points_redeemed=total_points_redeemed,
        tier_distribution=tier_distribution,
        top_members=top_members_data
    )
