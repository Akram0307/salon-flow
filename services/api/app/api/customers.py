"""Customer Management Routes for Salon Flow API.

Handles customer operations including:
- Customer CRUD operations
- Booking history
- Loyalty points management
- Membership tracking
"""

# Standard library imports
from datetime import datetime
from typing import Optional, List

# Third-party imports
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
import structlog

# Local imports
from app.api.dependencies import (
    get_current_user,
    get_salon_id,
    AuthContext,
    require_staff,
    verify_customer_access,
)
from app.models import CustomerModel, BookingModel, LoyaltyModel, MembershipModel
from app.schemas import (
    CustomerCreate,
    CustomerUpdate,
    Customer,
    CustomerSummary,
    CustomerSearch,
    LoyaltyTransactionCreate,
    LoyaltyTransaction,
    LoyaltyTransactionType,
    Membership,
    BookingSummary,
    PaginatedResponse,
)

logger = structlog.get_logger()
router = APIRouter(tags=["Customer Management"])


# ============================================================================
# Request/Response Schemas
# ============================================================================

class LoyaltyEarnRequest(BaseModel):
    """Loyalty points earn request.
    
    Attributes:
        amount: Amount spent in INR
        booking_id: Associated booking ID (optional)
        description: Transaction description (optional)
    """
    amount: float = Field(..., ge=0, description="Amount spent in INR")
    booking_id: Optional[str] = Field(None, description="Associated booking ID")
    description: Optional[str] = Field(None, description="Transaction description")


class LoyaltyRedeemRequest(BaseModel):
    """Loyalty points redeem request.
    
    Attributes:
        points: Points to redeem
        booking_id: Associated booking ID (optional)
        description: Transaction description (optional)
    """
    points: int = Field(..., ge=1, description="Points to redeem")
    booking_id: Optional[str] = Field(None, description="Associated booking ID")
    description: Optional[str] = Field(None, description="Transaction description")


class LoyaltyBalanceResponse(BaseModel):
    """Loyalty balance response.
    
    Attributes:
        customer_id: Customer's unique identifier
        total_points: Total points earned
        available_points: Points available for redemption
        pending_points: Points pending activation
        expired_points: Points that have expired
        tier: Customer's loyalty tier
        next_tier_points: Points needed for next tier
    """
    customer_id: str
    total_points: int
    available_points: int
    pending_points: int
    expired_points: int
    tier: str
    next_tier_points: int


# ============================================================================
# Routes
# ============================================================================

@router.get(
    "/",
    response_model=PaginatedResponse[CustomerSummary],
    summary="List customers",
    description="List all customers with pagination and search support.",
)
async def list_customers(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by name, phone, or email"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(get_current_user),
) -> PaginatedResponse[CustomerSummary]:
    """List customers with pagination and filtering.
    
    Supports:
    - Text search across name, phone, email
    - Active/inactive filtering
    - Cursor-based pagination
    
    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page
        search: Search string for name, phone, or email
        is_active: Filter by active status
        salon_id: Current salon ID from auth context
        current_user: Authenticated user context
        
    Returns:
        Paginated list of customer summaries
        
    Raises:
        HTTPException: 500 if database operation fails
    """
    try:
        customer_model = CustomerModel()
        
        # Build query
        query = CustomerSearch(
            salon_id=salon_id,
            search=search,
            is_active=is_active,
        )
        
        # Get paginated results
        result = await customer_model.search(
            query=query,
            page=page,
            page_size=page_size,
        )
        
        return result
        
    except Exception as e:
        logger.error("Failed to list customers", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Failed to retrieve customers", "code": "internal_error"},
        )


@router.post(
    "/",
    response_model=Customer,
    status_code=status.HTTP_201_CREATED,
    summary="Create customer",
    description="Create a new customer profile.",
)
async def create_customer(
    request: CustomerCreate,
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(require_staff),
) -> Customer:
    """Create a new customer.
    
    Creates a customer profile with optional preferences and initial loyalty points.
    
    Args:
        request: Customer creation data
        salon_id: Current salon ID from auth context
        current_user: Authenticated staff user context
        
    Returns:
        Created customer profile
        
    Raises:
        HTTPException: 400 if customer with same phone exists, 500 on database error
    """
    try:
        customer_model = CustomerModel()
        
        # Check for existing customer with same phone/email
        if request.phone:
            existing = await customer_model.get_by_phone(request.phone, salon_id)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={"message": "Customer with this phone number already exists", "code": "duplicate_phone"},
                )
        
        # Set salon_id from context
        customer_data = request.model_copy(update={
            "salon_id": salon_id,
        })
        
        customer = await customer_model.create(customer_data)
        
        logger.info(
            "Customer created",
            customer_id=customer.customer_id,
            salon_id=salon_id,
            created_by=current_user.uid,
        )
        
        return customer
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create customer", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Failed to create customer", "code": "internal_error"},
        )


@router.get(
    "/{customer_id}",
    response_model=Customer,
    summary="Get customer",
    description="Get detailed customer information.",
)
async def get_customer(
    customer_id: str,
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(get_current_user),
) -> Customer:
    """Get customer by ID.
    
    Args:
        customer_id: Customer's unique identifier
        salon_id: Current salon ID from auth context
        current_user: Authenticated user context
        
    Returns:
        Customer profile details
        
    Raises:
        HTTPException: 404 if customer not found, 403 if access denied
    """
    try:
        customer = await verify_customer_access(customer_id, salon_id)
        return customer
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get customer", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Failed to retrieve customer", "code": "internal_error"},
        )


@router.put(
    "/{customer_id}",
    response_model=Customer,
    summary="Update customer",
    description="Update customer information.",
)
async def update_customer(
    customer_id: str,
    request: CustomerUpdate,
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(require_staff),
) -> Customer:
    """Update customer profile.
    
    Args:
        customer_id: Customer's unique identifier
        request: Customer update data
        salon_id: Current salon ID from auth context
        current_user: Authenticated staff user context
        
    Returns:
        Updated customer profile
        
    Raises:
        HTTPException: 404 if customer not found, 403 if access denied
    """
    try:
        customer_model = CustomerModel()
        
        # Verify customer exists and belongs to salon
        existing = await verify_customer_access(customer_id, salon_id)
        
        # Update customer
        updated = await customer_model.update(customer_id, request)
        
        logger.info(
            "Customer updated",
            customer_id=existing.customer_id,
            updated_by=current_user.uid,
        )
        
        return updated
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update customer", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Failed to update customer", "code": "internal_error"},
        )


@router.delete(
    "/{customer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete customer",
    description="Soft delete a customer (mark as inactive).",
)
async def delete_customer(
    customer_id: str,
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(require_staff),
) -> None:
    """Soft delete customer by marking as inactive.
    
    Args:
        customer_id: Customer's unique identifier
        salon_id: Current salon ID from auth context
        current_user: Authenticated staff user context
        
    Raises:
        HTTPException: 404 if customer not found, 403 if access denied
    """
    try:
        customer_model = CustomerModel()
        
        # Verify customer exists and belongs to salon
        existing = await verify_customer_access(customer_id, salon_id)
        
        # Soft delete
        await customer_model.soft_delete(customer_id)
        
        logger.info(
            "Customer deleted",
            customer_id=existing.customer_id,
            deleted_by=current_user.uid,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete customer", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Failed to delete customer", "code": "internal_error"},
        )


@router.get(
    "/{customer_id}/bookings",
    response_model=PaginatedResponse[BookingSummary],
    summary="Get customer bookings",
    description="Get booking history for a customer.",
)
async def get_customer_bookings(
    customer_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(get_current_user),
) -> PaginatedResponse[BookingSummary]:
    """Get customer's booking history.
    
    Args:
        customer_id: Customer's unique identifier
        page: Page number (1-indexed)
        page_size: Number of items per page
        status_filter: Filter by booking status
        salon_id: Current salon ID from auth context
        current_user: Authenticated user context
        
    Returns:
        Paginated list of booking summaries
        
    Raises:
        HTTPException: 404 if customer not found, 403 if access denied
    """
    try:
        # Verify customer belongs to salon
        customer = await verify_customer_access(customer_id, salon_id)
        
        # Get bookings
        booking_model = BookingModel()
        bookings = await booking_model.get_by_customer(
            customer_id=customer.customer_id,
            salon_id=salon_id,
            status=status_filter,
            page=page,
            page_size=page_size,
        )
        
        return bookings
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get customer bookings", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Failed to retrieve bookings", "code": "internal_error"},
        )


@router.get(
    "/{customer_id}/loyalty",
    response_model=LoyaltyBalanceResponse,
    summary="Get loyalty balance",
    description="Get customer's loyalty points balance.",
)
async def get_customer_loyalty(
    customer_id: str,
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(get_current_user),
) -> LoyaltyBalanceResponse:
    """Get customer's loyalty points balance.
    
    Args:
        customer_id: Customer's unique identifier
        salon_id: Current salon ID from auth context
        current_user: Authenticated user context
        
    Returns:
        Loyalty balance and tier information
        
    Raises:
        HTTPException: 404 if customer not found, 403 if access denied
    """
    try:
        # Verify customer belongs to salon
        customer = await verify_customer_access(customer_id, salon_id)
        
        # Get loyalty balance
        loyalty_model = LoyaltyModel()
        balance = await loyalty_model.get_customer_balance(customer_id, salon_id)
        
        return LoyaltyBalanceResponse(
            customer_id=customer.customer_id,
            total_points=balance.get("total_points", 0),
            available_points=balance.get("available_points", 0),
            pending_points=balance.get("pending_points", 0),
            expired_points=balance.get("expired_points", 0),
            tier=balance.get("tier", "bronze"),
            next_tier_points=balance.get("next_tier_points", 100),
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get loyalty balance", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Failed to retrieve loyalty balance", "code": "internal_error"},
        )


@router.post(
    "/{customer_id}/loyalty/earn",
    response_model=LoyaltyTransaction,
    status_code=status.HTTP_201_CREATED,
    summary="Earn loyalty points",
    description="Add loyalty points for a customer based on spending.",
)
async def earn_loyalty_points(
    customer_id: str,
    request: LoyaltyEarnRequest,
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(require_staff),
) -> LoyaltyTransaction:
    """Earn loyalty points.
    
    Points are calculated as: 1 point per ₹10 spent.
    
    Args:
        customer_id: Customer's unique identifier
        request: Loyalty earn request with amount spent
        salon_id: Current salon ID from auth context
        current_user: Authenticated staff user context
        
    Returns:
        Created loyalty transaction
        
    Raises:
        HTTPException: 400 if amount too low, 404 if customer not found
    """
    try:
        # Verify customer belongs to salon
        customer = await verify_customer_access(customer_id, salon_id)
        
        # Calculate points (1 point per ₹10)
        points = int(request.amount / 10)
        
        if points <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": "Amount too low to earn points", "code": "amount_too_low"},
            )
        
        # Create loyalty transaction
        loyalty_model = LoyaltyModel()
        transaction_data = LoyaltyTransactionCreate(
            salon_id=salon_id,
            customer_id=customer.customer_id,
            transaction_type=LoyaltyTransactionType.EARN,
            points=points,
            reference_type="booking" if request.booking_id else "manual",
            reference_id=request.booking_id,
            description=request.description or f"Earned {points} points for ₹{request.amount} spend",
            created_by=current_user.uid,
        )
        
        transaction = await loyalty_model.create(transaction_data)
        
        logger.info(
            "Loyalty points earned",
            customer_id=customer.customer_id,
            points=points,
            amount=request.amount,
        )
        
        return transaction
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to earn loyalty points", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Failed to add loyalty points", "code": "internal_error"},
        )


@router.post(
    "/{customer_id}/loyalty/redeem",
    response_model=LoyaltyTransaction,
    status_code=status.HTTP_201_CREATED,
    summary="Redeem loyalty points",
    description="Redeem loyalty points for a customer.",
)
async def redeem_loyalty_points(
    customer_id: str,
    request: LoyaltyRedeemRequest,
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(require_staff),
) -> LoyaltyTransaction:
    """Redeem loyalty points.
    
    Points can be redeemed for discounts or services.
    
    Args:
        customer_id: Customer's unique identifier
        request: Loyalty redeem request with points to redeem
        salon_id: Current salon ID from auth context
        current_user: Authenticated staff user context
        
    Returns:
        Created loyalty redemption transaction
        
    Raises:
        HTTPException: 400 if insufficient points, 404 if customer not found
    """
    try:
        # Verify customer belongs to salon
        customer = await verify_customer_access(customer_id, salon_id)
        
        # Check available balance
        loyalty_model = LoyaltyModel()
        balance = await loyalty_model.get_customer_balance(customer_id, salon_id)
        available = balance.get("available_points", 0)
        
        if request.points > available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": f"Insufficient points. Available: {available}", "code": "insufficient_points"},
            )
        
        # Create redemption transaction
        transaction_data = LoyaltyTransactionCreate(
            salon_id=salon_id,
            customer_id=customer.customer_id,
            transaction_type=LoyaltyTransactionType.REDEEM,
            points=-request.points,  # Negative for redemption
            reference_type="booking" if request.booking_id else "manual",
            reference_id=request.booking_id,
            description=request.description or f"Redeemed {request.points} points",
            created_by=current_user.uid,
        )
        
        transaction = await loyalty_model.create(transaction_data)
        
        logger.info(
            "Loyalty points redeemed",
            customer_id=customer.customer_id,
            points=request.points,
        )
        
        return transaction
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to redeem loyalty points", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Failed to redeem loyalty points", "code": "internal_error"},
        )


@router.get(
    "/{customer_id}/membership",
    response_model=Optional[Membership],
    summary="Get customer membership",
    description="Get customer's active membership details.",
)
async def get_customer_membership(
    customer_id: str,
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(get_current_user),
) -> Optional[Membership]:
    """Get customer's active membership.
    
    Args:
        customer_id: Customer's unique identifier
        salon_id: Current salon ID from auth context
        current_user: Authenticated user context
        
    Returns:
        Active membership details or None if no active membership
        
    Raises:
        HTTPException: 404 if customer not found, 403 if access denied
    """
    try:
        # Verify customer belongs to salon
        await verify_customer_access(customer_id, salon_id)
        
        # Get active membership
        membership_model = MembershipModel()
        membership = await membership_model.get_active_for_customer(customer_id, salon_id)
        
        return membership
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get membership", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Failed to retrieve membership", "code": "internal_error"},
        )


__all__ = [
    "router",
    "LoyaltyEarnRequest",
    "LoyaltyRedeemRequest",
    "LoyaltyBalanceResponse",
]
