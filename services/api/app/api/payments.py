"""Payment Management Routes for Salon Flow API.

Handles payment operations including:
- Payment processing
- Invoice generation
- Revenue reporting
"""
from datetime import datetime, date
from decimal import Decimal
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
from app.models import PaymentModel, BookingModel
from app.schemas import (
    PaymentUpdate,
    PaymentCreate,
    Payment,
    PaymentSummary,
    PaymentMethod,
    PaymentStatus,
    DailyRevenue,
    PaginatedResponse,
)

logger = structlog.get_logger()
router = APIRouter(prefix="/payments", tags=["Payment Management"])


# ============================================================================
# Request/Response Schemas
# ============================================================================

class InvoiceResponse(BaseModel):
    """Invoice response."""
    invoice_number: str
    payment_id: str
    salon_name: str
    salon_address: str
    customer_name: str
    customer_phone: Optional[str]
    items: List[dict]
    subtotal: float
    gst_amount: float
    total: float
    payment_method: str
    payment_status: str
    created_at: datetime


class MonthlyRevenueResponse(BaseModel):
    """Monthly revenue response."""
    month: str
    year: int
    total_revenue: float
    total_payments: int
    by_payment_method: dict
    by_service_category: dict
    comparison_to_last_month: Optional[float]


# ============================================================================
# Routes
# ============================================================================

@router.get(
    "",
    response_model=PaginatedResponse[PaymentSummary],
    summary="List payments",
    description="List all payments with pagination and filtering.",
)
async def list_payments(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    start_date: Optional[date] = Query(None, description="Filter from date"),
    end_date: Optional[date] = Query(None, description="Filter to date"),
    payment_method: Optional[PaymentMethod] = Query(None, description="Filter by method"),
    status_filter: Optional[PaymentStatus] = Query(None, alias="status", description="Filter by status"),
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(get_current_user),
):
    """List payments with pagination and filtering."""
    try:
        payment_model = PaymentModel()
        
        result = await payment_model.search(
            salon_id=salon_id,
            start_date=start_date,
            end_date=end_date,
            payment_method=payment_method,
            status=status_filter,
            page=page,
            page_size=page_size,
        )
        
        return result
        
    except Exception as e:
        logger.error("Failed to list payments", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve payments",
        )


@router.post(
    "",
    response_model=Payment,
    status_code=status.HTTP_201_CREATED,
    summary="Create payment",
    description="Process a new payment.",
)
async def create_payment(
    request: PaymentCreate,
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(require_staff),
):
    """Create a new payment.
    
    Processes payment and updates booking status.
    """
    try:
        payment_model = PaymentModel()
        booking_model = BookingModel()
        
        # Verify booking exists if provided
        if request.booking_id:
            booking = await booking_model.get(request.booking_id)
            if not booking or booking.salon_id != salon_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Booking not found",
                )
        
        # Calculate GST (5%)
        gst_rate = Decimal("0.05")
        gst_amount = request.subtotal * gst_rate
        total_amount = request.subtotal + gst_amount
        
        # Set salon_id from context
        payment_data = request.model_copy(update={
            "salon_id": salon_id,
            "gst_amount": gst_amount,
            "total_amount": total_amount,
            "status": PaymentStatus.COMPLETED,
        })
        
        payment = await payment_model.create(payment_data)
        
        # Update booking payment status if linked
        if request.booking_id:
            await booking_model.update(request.booking_id, {
                "payment_id": payment.id,
                "payment_status": PaymentStatus.COMPLETED,
            })
        
        logger.info(
            "Payment created",
            payment_id=payment.id,
            salon_id=salon_id,
            amount=request.subtotal,
            method=request.payment_method,
            created_by=current_user.uid,
        )
        
        return payment
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create payment", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process payment",
        )


@router.get(
    "/{payment_id}",
    response_model=Payment,
    summary="Get payment",
    description="Get detailed payment information.",
)
async def get_payment(
    payment_id: str,
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(get_current_user),
):
    """Get payment by ID."""
    try:
        payment_model = PaymentModel()
        payment = await payment_model.get(payment_id)
        
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found",
            )
        
        # Verify salon access
        if payment.salon_id != salon_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )
        
        return payment
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get payment", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve payment",
        )


@router.get(
    "/{payment_id}/invoice",
    response_model=InvoiceResponse,
    summary="Get invoice",
    description="Get invoice details for a payment.",
)
async def get_invoice(
    payment_id: str,
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(get_current_user),
):
    """Get invoice for a payment."""
    try:
        payment_model = PaymentModel()
        payment = await payment_model.get(payment_id)
        
        if not payment or payment.salon_id != salon_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found",
            )
        
        # Generate invoice
        invoice = await payment_model.generate_invoice(payment_id)
        
        return InvoiceResponse(
            invoice_number=invoice.get("invoice_number", f"INV-{payment_id[:8]}"),
            payment_id=payment_id,
            salon_name=invoice.get("salon_name", "Salon"),
            salon_address=invoice.get("salon_address", ""),
            customer_name=invoice.get("customer_name", "Customer"),
            customer_phone=invoice.get("customer_phone"),
            items=invoice.get("items", []),
            subtotal=payment.amount,
            gst_amount=payment.gst_amount or 0,
            total=payment.total_amount or payment.amount,
            payment_method=payment.payment_method.value,
            payment_status=payment.status.value,
            created_at=payment.created_at,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get invoice", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate invoice",
        )


@router.get(
    "/revenue/daily",
    response_model=DailyRevenue,
    summary="Get daily revenue",
    description="Get revenue summary for a specific day.",
)
async def get_daily_revenue(
    date_param: date = Query(..., alias="date", description="Date to get revenue for"),
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(require_manager),
):
    """Get daily revenue summary.
    
    Only managers and owners can view revenue.
    """
    try:
        payment_model = PaymentModel()
        revenue = await payment_model.get_daily_revenue(salon_id, date_param)
        
        return DailyRevenue(
            date=date_param,
            total_revenue=revenue.get("total_revenue", 0),
            total_payments=revenue.get("total_payments", 0),
            by_payment_method=revenue.get("by_payment_method", {}),
            by_service_category=revenue.get("by_service_category", {}),
            average_transaction=revenue.get("average_transaction", 0),
        )
        
    except Exception as e:
        logger.error("Failed to get daily revenue", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve revenue",
        )


@router.get(
    "/revenue/monthly",
    response_model=MonthlyRevenueResponse,
    summary="Get monthly revenue",
    description="Get revenue summary for a specific month.",
)
async def get_monthly_revenue(
    year: int = Query(..., ge=2020, le=2030, description="Year"),
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(require_manager),
):
    """Get monthly revenue summary.
    
    Only managers and owners can view revenue.
    """
    try:
        payment_model = PaymentModel()
        revenue = await payment_model.get_monthly_revenue(salon_id, year, month)
        
        return MonthlyRevenueResponse(
            month=f"{year}-{month:02d}",
            year=year,
            total_revenue=revenue.get("total_revenue", 0),
            total_payments=revenue.get("total_payments", 0),
            by_payment_method=revenue.get("by_payment_method", {}),
            by_service_category=revenue.get("by_service_category", {}),
            comparison_to_last_month=revenue.get("comparison_to_last_month"),
        )
        
    except Exception as e:
        logger.error("Failed to get monthly revenue", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve revenue",
        )


@router.put(
    "/{payment_id}",
    response_model=Payment,
    summary="Update payment",
    description="Update payment information (tip, status, notes).",
)
async def update_payment(
    payment_id: str,
    request: PaymentUpdate,
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(require_staff),
):
    """Update payment.
    
    Staff can update tips and notes. Only managers can refund.
    """
    try:
        payment_model = PaymentModel()
        
        # Verify payment exists and belongs to salon
        existing = await payment_model.get(payment_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found",
            )
        
        if existing.salon_id != salon_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )
        
        # Check permission for refund
        if request.payment_status == PaymentStatus.REFUNDED:
            if not current_user.has_permission("manager"):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only managers can process refunds",
                )
        
        # Update payment
        update_data = request.model_dump(exclude_unset=True)
        updated = await payment_model.update(payment_id, update_data)
        
        logger.info(
            "Payment updated",
            payment_id=payment_id,
            updated_by=current_user.uid,
        )
        
        return updated
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update payment", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update payment",
        )
