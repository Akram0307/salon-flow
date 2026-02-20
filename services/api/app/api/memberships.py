"""Membership Management Routes for Salon Flow API.

Handles membership operations including:
- Membership CRUD operations
- Renewal management
- Expiring memberships tracking
"""
from datetime import datetime, date, timedelta
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
import structlog

from app.api.dependencies import (
    get_current_user,
    get_salon_id,
    AuthContext,
    require_staff,
    require_manager,
)
from app.models import MembershipModel, CustomerModel
from app.schemas import (
    MembershipCreate,
    MembershipUpdate,
    Membership,
    MembershipSummary,
    MembershipStatus,
    MembershipType,
    PaginatedResponse,
)

logger = structlog.get_logger()
router = APIRouter(prefix="/memberships", tags=["Membership Management"])


# ============================================================================
# Request/Response Schemas
# ============================================================================

class RenewMembershipRequest(BaseModel):
    """Membership renewal request."""
    duration_months: int = Field(..., ge=1, le=12, description="Renewal duration in months")
    payment_method: Optional[str] = None
    notes: Optional[str] = None


class RenewMembershipResponse(BaseModel):
    """Membership renewal response."""
    membership_id: str
    old_end_date: date
    new_end_date: date
    duration_months: int
    status: str


class ExpiringMembershipResponse(BaseModel):
    """Expiring membership response."""
    membership_id: str
    customer_id: str
    customer_name: str
    customer_phone: Optional[str]
    membership_type: str
    end_date: date
    days_remaining: int
    auto_renew: bool


# ============================================================================
# Routes
# ============================================================================

@router.get(
    "",
    response_model=PaginatedResponse[MembershipSummary],
    summary="List memberships",
    description="List all memberships with pagination and filtering.",
)
async def list_memberships(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status_filter: Optional[MembershipStatus] = Query(None, alias="status", description="Filter by status"),
    membership_type: Optional[MembershipType] = Query(None, description="Filter by type"),
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(get_current_user),
):
    """List memberships with pagination and filtering."""
    try:
        membership_model = MembershipModel()
        
        result = await membership_model.search(
            salon_id=salon_id,
            status=status_filter,
            membership_type=membership_type,
            page=page,
            page_size=page_size,
        )
        
        return result
        
    except Exception as e:
        logger.error("Failed to list memberships", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve memberships",
        )


@router.post(
    "",
    response_model=Membership,
    status_code=status.HTTP_201_CREATED,
    summary="Create membership",
    description="Create a new membership for a customer.",
)
async def create_membership(
    request: MembershipCreate,
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(require_staff),
):
    """Create a new membership.
    
    Validates:
    - Customer exists
    - Customer doesn't have an active membership
    """
    try:
        membership_model = MembershipModel()
        customer_model = CustomerModel()
        
        # Verify customer exists
        customer = await customer_model.get(request.customer_id)
        if not customer or customer.salon_id != salon_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found",
            )
        
        # Check for existing active membership
        existing = await membership_model.get_active_for_customer(request.customer_id, salon_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer already has an active membership",
            )
        
        # Calculate end date based on duration
        start_date = request.start_date or date.today()
        end_date = start_date + timedelta(days=30 * request.duration_months)
        
        # Set salon_id from context
        membership_data = request.model_copy(update={
            "salon_id": salon_id,
            "start_date": start_date,
            "end_date": end_date,
            "status": MembershipStatus.ACTIVE,
        })
        
        membership = await membership_model.create(membership_data)
        
        logger.info(
            "Membership created",
            membership_id=membership.id,
            salon_id=salon_id,
            customer_id=request.customer_id,
            created_by=current_user.uid,
        )
        
        return membership
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create membership", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create membership",
        )


@router.get(
    "/expiring",
    response_model=List[ExpiringMembershipResponse],
    summary="Get expiring memberships",
    description="Get memberships expiring within a specified number of days.",
)
async def get_expiring_memberships(
    days: int = Query(15, ge=1, le=90, description="Days threshold for expiry"),
    limit: int = Query(50, ge=1, le=200, description="Maximum results"),
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(require_staff),
):
    """Get memberships expiring soon.
    
    Default: memberships expiring within 15 days.
    Used for renewal reminders.
    """
    try:
        membership_model = MembershipModel()
        customer_model = CustomerModel()
        
        # Get expiring memberships
        expiring = await membership_model.get_expiring(salon_id, days, limit)
        
        result = []
        for membership in expiring:
            # Get customer details
            customer = await customer_model.get(membership.customer_id)
            
            days_remaining = (membership.end_date - date.today()).days
            
            result.append(ExpiringMembershipResponse(
                membership_id=membership.id,
                customer_id=membership.customer_id,
                customer_name=customer.name if customer else "Unknown",
                customer_phone=customer.phone if customer else None,
                membership_type=membership.membership_type.value,
                end_date=membership.end_date,
                days_remaining=days_remaining,
                auto_renew=membership.auto_renew,
            ))
        
        return result
        
    except Exception as e:
        logger.error("Failed to get expiring memberships", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve expiring memberships",
        )


@router.get(
    "/{membership_id}",
    response_model=Membership,
    summary="Get membership",
    description="Get detailed membership information.",
)
async def get_membership(
    membership_id: str,
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(get_current_user),
):
    """Get membership by ID."""
    try:
        membership_model = MembershipModel()
        membership = await membership_model.get(membership_id)
        
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Membership not found",
            )
        
        # Verify salon access
        if membership.salon_id != salon_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )
        
        return membership
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get membership", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve membership",
        )


@router.put(
    "/{membership_id}",
    response_model=Membership,
    summary="Update membership",
    description="Update membership information.",
)
async def update_membership(
    membership_id: str,
    request: MembershipUpdate,
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(require_manager),
):
    """Update membership.
    
    Managers and owners can update memberships.
    """
    try:
        membership_model = MembershipModel()
        
        # Verify membership exists and belongs to salon
        existing = await membership_model.get(membership_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Membership not found",
            )
        
        if existing.salon_id != salon_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )
        
        # Update membership
        updated = await membership_model.update(membership_id, request)
        
        logger.info(
            "Membership updated",
            membership_id=membership_id,
            updated_by=current_user.uid,
        )
        
        return updated
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update membership", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update membership",
        )


@router.post(
    "/{membership_id}/renew",
    response_model=RenewMembershipResponse,
    summary="Renew membership",
    description="Renew an existing membership.",
)
async def renew_membership(
    membership_id: str,
    request: RenewMembershipRequest,
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(require_staff),
):
    """Renew a membership.
    
    Extends the membership end date by the specified duration.
    """
    try:
        membership_model = MembershipModel()
        
        # Verify membership exists and belongs to salon
        existing = await membership_model.get(membership_id)
        if not existing or existing.salon_id != salon_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Membership not found",
            )
        
        # Calculate new end date
        # If membership is expired, start from today; otherwise extend from current end date
        base_date = existing.end_date if existing.end_date >= date.today() else date.today()
        new_end_date = base_date + timedelta(days=30 * request.duration_months)
        
        # Update membership
        update_data = MembershipUpdate(
            end_date=new_end_date,
            status=MembershipStatus.ACTIVE,
            notes=f"Renewed for {request.duration_months} months. {request.notes or ''}",
        )
        
        await membership_model.update(membership_id, update_data)
        
        logger.info(
            "Membership renewed",
            membership_id=membership_id,
            old_end_date=existing.end_date,
            new_end_date=new_end_date,
            duration_months=request.duration_months,
            renewed_by=current_user.uid,
        )
        
        return RenewMembershipResponse(
            membership_id=membership_id,
            old_end_date=existing.end_date,
            new_end_date=new_end_date,
            duration_months=request.duration_months,
            status=MembershipStatus.ACTIVE.value,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to renew membership", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to renew membership",
        )
