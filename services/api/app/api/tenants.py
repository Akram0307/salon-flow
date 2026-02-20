"""Tenant/Salon Management Routes for Salon Flow API.

Handles salon operations including:
- Salon onboarding and management
- Layout configuration
- Settings management
- Subscription management

Optimized with Redis caching for frequently accessed data.
"""
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
import structlog

from app.api.dependencies import (
    get_current_user,
    get_salon_id,
    AuthContext,
    require_owner,
    require_manager,
)
from app.models import SalonModel
from app.schemas import (
    SalonCreate,
    SalonUpdate,
    Salon,
    SalonSummary,
    SalonLayout,
    SalonSettings,
    SalonSubscription,
    SubscriptionPlan,
    SubscriptionStatus,
)
from app.core.redis import redis_client, CacheConfig

logger = structlog.get_logger()
router = APIRouter(prefix="/tenants", tags=["Tenant Management"])


# ============================================================================
# Cache Keys
# ============================================================================

def salon_cache_key(salon_id: str) -> str:
    return f"{CacheConfig.PREFIX_SALON}:{salon_id}"

def salon_layout_cache_key(salon_id: str) -> str:
    return f"{CacheConfig.PREFIX_SALON}:{salon_id}:layout"

def salon_settings_cache_key(salon_id: str) -> str:
    return f"{CacheConfig.PREFIX_SALON}:{salon_id}:settings"

def salon_business_settings_cache_key(salon_id: str) -> str:
    return f"{CacheConfig.PREFIX_SALON}:{salon_id}:business_settings"


# ============================================================================
# Request/Response Schemas
# ============================================================================

class LayoutUpdateRequest(BaseModel):
    """Salon layout update request."""
    mens_chairs: int = Field(..., ge=0, le=20)
    womens_chairs: int = Field(..., ge=0, le=20)
    service_rooms: int = Field(..., ge=0, le=10)
    bridal_room: bool = Field(default=True)
    spa_rooms: int = Field(default=1, ge=0, le=5)
    waiting_capacity: int = Field(default=10, ge=1)


class SettingsUpdateRequest(BaseModel):
    """Salon settings update request."""
    # Booking settings
    booking_buffer_minutes: Optional[int] = Field(None, ge=0, le=60)
    max_advance_booking_days: Optional[int] = Field(None, ge=1, le=90)
    cancellation_hours: Optional[int] = Field(None, ge=0, le=72)
    # Notification settings
    reminder_hours_before: Optional[int] = Field(None, ge=1, le=48)
    send_birthday_offers: Optional[bool] = None
    send_rebooking_reminders: Optional[bool] = None
    rebooking_days_after: Optional[int] = Field(None, ge=1, le=30)
    # Payment settings
    accept_cash: Optional[bool] = None
    accept_upi: Optional[bool] = None
    accept_card: Optional[bool] = None
    accept_wallet: Optional[bool] = None
    # WhatsApp settings
    whatsapp_enabled: Optional[bool] = None
    whatsapp_business_number: Optional[str] = None
    # Theme settings
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    logo_url: Optional[str] = None


class SubscriptionUpdateRequest(BaseModel):
    """Subscription update request."""
    plan: SubscriptionPlan
    billing_cycle: Optional[str] = "monthly"


class BusinessSettingsUpdateRequest(BaseModel):
    """Business settings update request (embedded in Salon model)."""
    gst_rate: Optional[float] = Field(None, ge=0, le=100)
    loyalty_rate: Optional[float] = Field(None, ge=0, le=1)
    loyalty_expiry_months: Optional[int] = Field(None, ge=1, le=24)
    membership_renewal_days: Optional[int] = Field(None, ge=1, le=30)
    late_arrival_grace_minutes: Optional[int] = Field(None, ge=0, le=60)


class BusinessSettings(BaseModel):
    """Business settings response."""
    gst_rate: float
    loyalty_rate: float
    loyalty_expiry_months: int
    membership_renewal_days: int
    late_arrival_grace_minutes: int


# ============================================================================
# Routes
# ============================================================================

@router.post(
    "",
    response_model=Salon,
    status_code=status.HTTP_201_CREATED,
    summary="Create new salon",
    description="Create a new salon tenant during onboarding.",
)
async def create_salon(
    request: SalonCreate,
    current_user: AuthContext = Depends(require_owner),
):
    """Create a new salon tenant.

    This endpoint is used during onboarding to create a new salon.
    Only users with owner role can create salons.
    """
    try:
        salon_model = SalonModel()

        # Set owner from authenticated user
        salon_data = request.model_copy(update={
            "owner_id": current_user.uid,
        })

        salon = await salon_model.create(salon_data)

        logger.info(
            "Salon created",
            salon_id=salon.id,
            owner_id=current_user.uid,
        )

        return salon

    except Exception as e:
        logger.error("Failed to create salon", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create salon: {str(e)}",
        )


@router.get(
    "/{salon_id}",
    response_model=Salon,
    summary="Get salon details",
    description="Get detailed information about a specific salon.",
)
async def get_salon(
    salon_id: str,
    current_user: AuthContext = Depends(get_current_user),
):
    """Get salon details by ID with caching.

    Users can only access their own salon.
    Salon configs are cached for 1 hour.
    """
    try:
        # Verify user belongs to this salon
        if current_user.salon_id != salon_id and not current_user.is_owner:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this salon",
            )

        # Try cache first
        cache_key = salon_cache_key(salon_id)
        if redis_client.is_connected:
            cached = await redis_client.get(cache_key)
            if cached:
                logger.debug("Salon cache hit", salon_id=salon_id)
                return Salon.model_validate(cached)

        salon_model = SalonModel()
        salon = await salon_model.get(salon_id)

        if not salon:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Salon not found",
            )

        # Cache the result
        if redis_client.is_connected:
            await redis_client.set(
                cache_key,
                salon.model_dump(),
                expire=CacheConfig.SALON_CONFIG_TTL
            )

        return salon

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get salon", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve salon",
        )


@router.put(
    "/{salon_id}",
    response_model=Salon,
    summary="Update salon",
    description="Update salon information.",
)
async def update_salon(
    salon_id: str,
    request: SalonUpdate,
    current_user: AuthContext = Depends(require_manager),
):
    """Update salon information.

    Only managers and owners can update salon details.
    Invalidates cache on update.
    """
    try:
        # Verify user belongs to this salon
        if current_user.salon_id != salon_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this salon",
            )

        salon_model = SalonModel()

        # Check if salon exists
        existing = await salon_model.get(salon_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Salon not found",
            )

        # Update salon
        updated = await salon_model.update(salon_id, request)

        # Invalidate cache
        await redis_client.invalidate_salon_cache(salon_id)

        logger.info(
            "Salon updated",
            salon_id=salon_id,
            user_id=current_user.uid,
        )

        return updated

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update salon", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update salon",
        )


@router.get(
    "/{salon_id}/layout",
    response_model=SalonLayout,
    summary="Get salon layout",
    description="Get the salon's layout configuration including chairs and rooms.",
)
async def get_salon_layout(
    salon_id: str,
    current_user: AuthContext = Depends(get_current_user),
):
    """Get salon layout configuration with caching."""
    try:
        if current_user.salon_id != salon_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        # Try cache first
        cache_key = salon_layout_cache_key(salon_id)
        if redis_client.is_connected:
            cached = await redis_client.get(cache_key)
            if cached:
                logger.debug("Layout cache hit", salon_id=salon_id)
                return SalonLayout.model_validate(cached)

        salon_model = SalonModel()
        salon = await salon_model.get(salon_id)

        if not salon:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Salon not found",
            )

        layout = salon.layout

        # Cache the result
        if redis_client.is_connected:
            await redis_client.set(
                cache_key,
                layout.model_dump(),
                expire=CacheConfig.SALON_CONFIG_TTL
            )

        return layout

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get layout", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve layout",
        )


@router.put(
    "/{salon_id}/layout",
    response_model=SalonLayout,
    summary="Update salon layout",
    description="Update the salon's layout configuration.",
)
async def update_salon_layout(
    salon_id: str,
    request: LayoutUpdateRequest,
    current_user: AuthContext = Depends(require_owner),
):
    """Update salon layout configuration.

    Only owners can modify layout.
    Invalidates cache on update.
    """
    try:
        if current_user.salon_id != salon_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        salon_model = SalonModel()

        # Check if salon exists
        existing = await salon_model.get(salon_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Salon not found",
            )

        # Create layout object
        layout_data = SalonLayout(
            mens_chairs=request.mens_chairs,
            womens_chairs=request.womens_chairs,
            service_rooms=request.service_rooms,
            bridal_room=request.bridal_room,
            spa_rooms=request.spa_rooms,
            waiting_capacity=request.waiting_capacity,
        )

        # Update salon with new layout
        update_data = SalonUpdate(layout=layout_data)
        await salon_model.update(salon_id, update_data)

        # Invalidate cache
        await redis_client.delete(salon_cache_key(salon_id))
        await redis_client.delete(salon_layout_cache_key(salon_id))

        logger.info(
            "Salon layout updated",
            salon_id=salon_id,
        )

        return layout_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update layout", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update layout",
        )


@router.get(
    "/{salon_id}/settings",
    response_model=SalonSettings,
    summary="Get salon settings",
    description="Get the salon's operational settings.",
)
async def get_salon_settings(
    salon_id: str,
    current_user: AuthContext = Depends(get_current_user),
):
    """Get salon settings with caching."""
    try:
        if current_user.salon_id != salon_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        # Try cache first
        cache_key = salon_settings_cache_key(salon_id)
        if redis_client.is_connected:
            cached = await redis_client.get(cache_key)
            if cached:
                logger.debug("Settings cache hit", salon_id=salon_id)
                return SalonSettings.model_validate(cached)

        salon_model = SalonModel()
        salon = await salon_model.get(salon_id)

        if not salon:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Salon not found",
            )

        settings = SalonSettings(salon_id=salon_id)

        # Cache the result
        if redis_client.is_connected:
            await redis_client.set(
                cache_key,
                settings.model_dump(),
                expire=CacheConfig.SALON_CONFIG_TTL
            )

        return settings

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get settings", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve settings",
        )


@router.put(
    "/{salon_id}/settings",
    response_model=SalonSettings,
    summary="Update salon settings",
    description="Update the salon's operational settings.",
)
async def update_salon_settings(
    salon_id: str,
    request: SettingsUpdateRequest,
    current_user: AuthContext = Depends(require_manager),
):
    """Update salon settings.

    Managers and owners can update settings.
    Invalidates cache on update.
    """
    try:
        if current_user.salon_id != salon_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        salon_model = SalonModel()
        salon = await salon_model.get(salon_id)

        if not salon:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Salon not found",
            )

        # Invalidate cache
        await redis_client.delete(salon_settings_cache_key(salon_id))

        logger.info(
            "Salon settings updated",
            salon_id=salon_id,
        )

        return SalonSettings(salon_id=salon_id, **request.model_dump(exclude_unset=True))

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update settings", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update settings",
        )


@router.get(
    "/{salon_id}/business-settings",
    response_model=BusinessSettings,
    summary="Get salon business settings",
    description="Get the salon's business settings (GST, loyalty, etc.).",
)
async def get_salon_business_settings(
    salon_id: str,
    current_user: AuthContext = Depends(get_current_user),
):
    """Get salon business settings with caching."""
    try:
        if current_user.salon_id != salon_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        # Try cache first
        cache_key = salon_business_settings_cache_key(salon_id)
        if redis_client.is_connected:
            cached = await redis_client.get(cache_key)
            if cached:
                logger.debug("Business settings cache hit", salon_id=salon_id)
                return BusinessSettings.model_validate(cached)

        salon_model = SalonModel()
        salon = await salon_model.get(salon_id)

        if not salon:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Salon not found",
            )

        settings = BusinessSettings(
            gst_rate=float(salon.gst_rate),
            loyalty_rate=float(salon.loyalty_rate),
            loyalty_expiry_months=salon.loyalty_expiry_months,
            membership_renewal_days=salon.membership_renewal_days,
            late_arrival_grace_minutes=salon.late_arrival_grace_minutes,
        )

        # Cache the result
        if redis_client.is_connected:
            await redis_client.set(
                cache_key,
                settings.model_dump(),
                expire=CacheConfig.SALON_CONFIG_TTL
            )

        return settings

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get business settings", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve business settings",
        )


@router.put(
    "/{salon_id}/business-settings",
    response_model=BusinessSettings,
    summary="Update salon business settings",
    description="Update the salon's business settings (GST, loyalty, etc.).",
)
async def update_salon_business_settings(
    salon_id: str,
    request: BusinessSettingsUpdateRequest,
    current_user: AuthContext = Depends(require_owner),
):
    """Update salon business settings.

    Only owners can modify business settings.
    Invalidates cache on update.
    """
    try:
        if current_user.salon_id != salon_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        salon_model = SalonModel()
        salon = await salon_model.get(salon_id)

        if not salon:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Salon not found",
            )

        # Build update data from request
        update_fields = request.model_dump(exclude_unset=True)
        update_data = SalonUpdate(**update_fields)

        # Save to salon
        await salon_model.update(salon_id, update_data)

        # Invalidate cache
        await redis_client.delete(salon_business_settings_cache_key(salon_id))

        logger.info(
            "Salon business settings updated",
            salon_id=salon_id,
        )

        # Return updated settings
        return BusinessSettings(
            gst_rate=update_fields.get('gst_rate', float(salon.gst_rate)),
            loyalty_rate=update_fields.get('loyalty_rate', float(salon.loyalty_rate)),
            loyalty_expiry_months=update_fields.get('loyalty_expiry_months', salon.loyalty_expiry_months),
            membership_renewal_days=update_fields.get('membership_renewal_days', salon.membership_renewal_days),
            late_arrival_grace_minutes=update_fields.get('late_arrival_grace_minutes', salon.late_arrival_grace_minutes),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update business settings", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update business settings",
        )


@router.get(
    "/{salon_id}/subscription",
    response_model=SalonSubscription,
    summary="Get salon subscription",
    description="Get the salon's subscription details.",
)
async def get_salon_subscription(
    salon_id: str,
    current_user: AuthContext = Depends(require_owner),
):
    """Get salon subscription details.

    Only owners can view subscription details.
    """
    try:
        if current_user.salon_id != salon_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        salon_model = SalonModel()
        salon = await salon_model.get(salon_id)

        if not salon:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Salon not found",
            )

        # Return subscription from embedded fields
        return SalonSubscription(
            plan=salon.subscription_plan,
            status=salon.subscription_status,
            current_period_end=salon.subscription_ends_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get subscription", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve subscription",
        )


@router.put(
    "/{salon_id}/subscription",
    response_model=SalonSubscription,
    summary="Update salon subscription",
    description="Update the salon's subscription plan.",
)
async def update_salon_subscription(
    salon_id: str,
    request: SubscriptionUpdateRequest,
    current_user: AuthContext = Depends(require_owner),
):
    """Update salon subscription.

    Only owners can modify subscription.
    """
    try:
        if current_user.salon_id != salon_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        salon_model = SalonModel()
        salon = await salon_model.get(salon_id)

        if not salon:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Salon not found",
            )

        # Update subscription fields
        update_data = SalonUpdate(
            subscription_plan=request.plan,
            subscription_status=SubscriptionStatus.ACTIVE,
        )
        await salon_model.update(salon_id, update_data)

        logger.info(
            "Salon subscription updated",
            salon_id=salon_id,
            plan=request.plan,
        )

        return SalonSubscription(
            plan=request.plan,
            status=SubscriptionStatus.ACTIVE,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update subscription", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update subscription",
        )
