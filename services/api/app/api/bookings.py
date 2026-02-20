"""Booking Management Routes for Salon Flow API.

Handles booking operations including:
- Booking CRUD operations
- Status lifecycle management
- Availability checking
- Time slot generation
"""

# Standard library imports
from datetime import datetime, date, timedelta
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
    require_manager,
    verify_booking_access,
)
from app.models import BookingModel, ServiceModel, StaffModel, CustomerModel
from app.schemas import (
    BookingCreate,
    BookingUpdate,
    Booking,
    BookingSummary,
    BookingStatus,
    BookingStatusUpdate,
    TimeSlot,
    PaginatedResponse,
)

logger = structlog.get_logger()
router = APIRouter(prefix="/bookings", tags=["Booking Management"])


# ============================================================================
# Request/Response Schemas
# ============================================================================

class CheckInRequest(BaseModel):
    """Check-in request.
    
    Attributes:
        notes: Optional notes for the check-in
    """
    notes: Optional[str] = None


class StartServiceRequest(BaseModel):
    """Start service request.
    
    Attributes:
        actual_start_time: Actual time service started
        notes: Optional notes
    """
    actual_start_time: Optional[datetime] = None
    notes: Optional[str] = None


class CompleteServiceRequest(BaseModel):
    """Complete service request.
    
    Attributes:
        actual_end_time: Actual time service completed
        notes: Optional notes
        customer_feedback: Customer feedback text
        rating: Rating from 1-5
    """
    actual_end_time: Optional[datetime] = None
    notes: Optional[str] = None
    customer_feedback: Optional[str] = None
    rating: Optional[int] = Field(None, ge=1, le=5)


class UpsellRequest(BaseModel):
    """Upsell service request.
    
    Attributes:
        service_id: Service ID to add as upsell
        staff_id: Staff ID for the upsell service
        notes: Optional notes
    """
    service_id: str
    staff_id: Optional[str] = None
    notes: Optional[str] = None


class AvailabilityRequest(BaseModel):
    """Availability check request.
    
    Attributes:
        service_id: Service ID to check
        staff_id: Optional staff ID
        date: Date to check
    """
    service_id: str
    staff_id: Optional[str] = None
    date: date


class AvailabilityResponse(BaseModel):
    """Availability check response.
    
    Attributes:
        service_id: Service ID checked
        staff_id: Staff ID checked
        date: Date checked
        available: Whether the slot is available
        available_slots: List of available time slots
        message: Optional message
    """
    service_id: str
    staff_id: Optional[str]
    date: date
    available: bool
    available_slots: List[TimeSlot]
    message: Optional[str] = None


class SlotsResponse(BaseModel):
    """Time slots response.
    
    Attributes:
        date: Date for the slots
        service_id: Service ID
        staff_id: Staff ID
        slots: List of available time slots
    """
    date: date
    service_id: str
    staff_id: Optional[str]
    slots: List[TimeSlot]


# ============================================================================
# Routes
# ============================================================================

@router.get(
    "",
    response_model=PaginatedResponse[BookingSummary],
    summary="List bookings",
    description="List all bookings with pagination and filtering.",
)
async def list_bookings(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    date_filter: Optional[date] = Query(None, alias="date", description="Filter by date"),
    status_filter: Optional[BookingStatus] = Query(None, alias="status", description="Filter by status"),
    staff_id: Optional[str] = Query(None, description="Filter by staff"),
    customer_id: Optional[str] = Query(None, description="Filter by customer"),
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(get_current_user),
) -> PaginatedResponse[BookingSummary]:
    """List bookings with pagination and filtering.
    
    Supports:
    - Date filtering
    - Status filtering
    - Staff filtering
    - Customer filtering
    
    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page
        date_filter: Filter by booking date
        status_filter: Filter by booking status
        staff_id: Filter by staff ID
        customer_id: Filter by customer ID
        salon_id: Current salon ID from auth context
        current_user: Authenticated user context
        
    Returns:
        Paginated list of booking summaries
        
    Raises:
        HTTPException: 500 if database operation fails
    """
    try:
        booking_model = BookingModel()
        
        result = await booking_model.search_bookings(
            salon_id=salon_id,
            date=date_filter,
            status=status_filter,
            staff_id=staff_id,
            customer_id=customer_id,
            page=page,
            page_size=page_size,
        )
        
        return result
        
    except Exception as e:
        logger.error("Failed to list bookings", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Failed to retrieve bookings", "code": "internal_error"},
        )


@router.post(
    "",
    response_model=Booking,
    status_code=status.HTTP_201_CREATED,
    summary="Create booking",
    description="Create a new booking.",
)
async def create_booking(
    request: BookingCreate,
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(require_staff),
) -> Booking:
    """Create a new booking.
    
    Validates:
    - Service exists and is active
    - Staff is available and has required skills
    - Time slot is available
    
    Args:
        request: Booking creation data
        salon_id: Current salon ID from auth context
        current_user: Authenticated staff user context
        
    Returns:
        Created booking
        
    Raises:
        HTTPException: 404 if service/staff not found, 409 if slot unavailable
    """
    try:
        booking_model = BookingModel()
        service_model = ServiceModel()
        staff_model = StaffModel()
        
        # Verify service exists
        service = await service_model.get(request.service_id)
        if not service or service.salon_id != salon_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": "Service not found", "code": "service_not_found"},
            )
        
        # Verify staff if specified
        if request.staff_id:
            staff = await staff_model.get(request.staff_id)
            if not staff or staff.salon_id != salon_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={"message": "Staff not found", "code": "staff_not_found"},
                )
            
            # Check if staff has the required skill
            if not any(s.service_id == request.service_id for s in (staff.skills.skills if staff.skills else [])):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={"message": "Staff does not have the required skill for this service", "code": "skill_mismatch"},
                )
        
        # Check availability
        is_available = await booking_model.check_availability(
            salon_id=salon_id,
            staff_id=request.staff_id,
            start_time=request.start_time,
            duration_minutes=service.duration.base_minutes,
        )
        
        if not is_available:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"message": "Time slot not available", "code": "slot_unavailable"},
            )
        
        # Set salon_id from context
        booking_data = request.model_copy(update={
            "salon_id": salon_id,
            "status": BookingStatus.PENDING,
        })
        
        booking = await booking_model.create(booking_data)
        
        logger.info(
            "Booking created",
            booking_id=booking.id,
            salon_id=salon_id,
            service_id=request.service_id,
            created_by=current_user.uid,
        )
        
        return booking
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create booking", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Failed to create booking", "code": "internal_error"},
        )


@router.get(
    "/availability",
    response_model=AvailabilityResponse,
    summary="Check availability",
    description="Check if a time slot is available for booking.",
)
async def check_availability(
    service_id: str = Query(..., description="Service ID"),
    staff_id: Optional[str] = Query(None, description="Staff ID (optional)"),
    date_param: date = Query(..., alias="date", description="Date to check"),
    time: Optional[str] = Query(None, description="Specific time (HH:MM)"),
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(get_current_user),
) -> AvailabilityResponse:
    """Check availability for a service on a specific date.
    
    Args:
        service_id: Service ID to check
        staff_id: Optional staff ID to check
        date_param: Date to check
        time: Optional specific time (HH:MM format)
        salon_id: Current salon ID from auth context
        current_user: Authenticated user context
        
    Returns:
        Availability information with available slots
        
    Raises:
        HTTPException: 404 if service not found
    """
    try:
        booking_model = BookingModel()
        service_model = ServiceModel()
        
        # Get service duration
        service = await service_model.get(service_id)
        if not service or service.salon_id != salon_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": "Service not found", "code": "service_not_found"},
            )
        
        # Get available slots
        slots = await booking_model.get_available_slots(
            salon_id=salon_id,
            service_id=service_id,
            staff_id=staff_id,
            date=date_param,
            duration_minutes=service.duration.base_minutes,
        )
        
        # Check specific time if provided
        available = True
        message = None
        
        if time:
            time_obj = datetime.strptime(time, "%H:%M").time()
            slot_datetime = datetime.combine(date_param, time_obj)
            
            available = await booking_model.check_availability(
                salon_id=salon_id,
                staff_id=staff_id,
                start_time=slot_datetime,
                duration_minutes=service.duration.base_minutes,
            )
            
            if not available:
                message = "Selected time slot is not available"
        
        return AvailabilityResponse(
            service_id=service_id,
            staff_id=staff_id,
            date=date_param,
            available=available,
            available_slots=slots,
            message=message,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to check availability", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Failed to check availability", "code": "internal_error"},
        )


@router.get(
    "/slots",
    response_model=SlotsResponse,
    summary="Get available time slots",
    description="Get all available time slots for a service on a specific date.",
)
async def get_available_slots(
    service_id: str = Query(..., description="Service ID"),
    staff_id: Optional[str] = Query(None, description="Staff ID (optional)"),
    date_param: date = Query(..., alias="date", description="Date to check"),
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(get_current_user),
) -> SlotsResponse:
    """Get available time slots for booking.
    
    Args:
        service_id: Service ID to check
        staff_id: Optional staff ID to check
        date_param: Date to check
        salon_id: Current salon ID from auth context
        current_user: Authenticated user context
        
    Returns:
        List of available time slots
        
    Raises:
        HTTPException: 404 if service not found
    """
    try:
        booking_model = BookingModel()
        service_model = ServiceModel()
        
        # Get service duration
        service = await service_model.get(service_id)
        if not service or service.salon_id != salon_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": "Service not found", "code": "service_not_found"},
            )
        
        # Get available slots
        slots = await booking_model.get_available_slots(
            salon_id=salon_id,
            service_id=service_id,
            staff_id=staff_id,
            date=date_param,
            duration_minutes=service.duration.base_minutes,
        )
        
        return SlotsResponse(
            date=date_param,
            service_id=service_id,
            staff_id=staff_id,
            slots=slots,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get slots", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Failed to retrieve time slots", "code": "internal_error"},
        )


@router.get(
    "/{booking_id}",
    response_model=Booking,
    summary="Get booking",
    description="Get detailed booking information.",
)
async def get_booking(
    booking_id: str,
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(get_current_user),
) -> Booking:
    """Get booking by ID.
    
    Args:
        booking_id: Booking's unique identifier
        salon_id: Current salon ID from auth context
        current_user: Authenticated user context
        
    Returns:
        Booking details
        
    Raises:
        HTTPException: 404 if booking not found, 403 if access denied
    """
    try:
        booking = await verify_booking_access(booking_id, salon_id)
        return booking
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get booking", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Failed to retrieve booking", "code": "internal_error"},
        )


@router.put(
    "/{booking_id}",
    response_model=Booking,
    summary="Update booking",
    description="Update booking information.",
)
async def update_booking(
    booking_id: str,
    request: BookingUpdate,
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(require_staff),
) -> Booking:
    """Update booking.
    
    Staff can update bookings.
    
    Args:
        booking_id: Booking's unique identifier
        request: Booking update data
        salon_id: Current salon ID from auth context
        current_user: Authenticated staff user context
        
    Returns:
        Updated booking
        
    Raises:
        HTTPException: 404 if booking not found, 400 if cannot modify
    """
    try:
        booking_model = BookingModel()
        
        # Verify booking exists and belongs to salon
        existing = await verify_booking_access(booking_id, salon_id)
        
        # Check if booking can be modified
        if existing.status in [BookingStatus.COMPLETED, BookingStatus.CANCELLED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": "Cannot modify completed or cancelled booking", "code": "invalid_status"},
            )
        
        # Update booking
        updated = await booking_model.update(booking_id, request)
        
        logger.info(
            "Booking updated",
            booking_id=booking_id,
            updated_by=current_user.uid,
        )
        
        return updated
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update booking", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Failed to update booking", "code": "internal_error"},
        )


@router.delete(
    "/{booking_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cancel booking",
    description="Cancel a booking.",
)
async def cancel_booking(
    booking_id: str,
    reason: Optional[str] = Query(None, description="Cancellation reason"),
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(require_staff),
) -> None:
    """Cancel a booking.
    
    Args:
        booking_id: Booking's unique identifier
        reason: Cancellation reason
        salon_id: Current salon ID from auth context
        current_user: Authenticated staff user context
        
    Raises:
        HTTPException: 404 if booking not found, 400 if cannot cancel
    """
    try:
        booking_model = BookingModel()
        
        # Verify booking exists and belongs to salon
        existing = await verify_booking_access(booking_id, salon_id)
        
        # Check if booking can be cancelled
        if existing.status in [BookingStatus.COMPLETED, BookingStatus.CANCELLED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": "Cannot cancel completed or already cancelled booking", "code": "invalid_status"},
            )
        
        # Update status to cancelled
        status_update = BookingStatusUpdate(
            status=BookingStatus.CANCELLED,
            notes=reason or "Cancelled by user",
        )
        await booking_model.update_status(booking_id, status_update)
        
        logger.info(
            "Booking cancelled",
            booking_id=booking_id,
            cancelled_by=current_user.uid,
            reason=reason,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to cancel booking", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Failed to cancel booking", "code": "internal_error"},
        )


@router.post(
    "/{booking_id}/check-in",
    response_model=Booking,
    summary="Check in customer",
    description="Mark customer as checked in for their booking.",
)
async def check_in_customer(
    booking_id: str,
    request: CheckInRequest,
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(require_staff),
) -> Booking:
    """Check in customer for their booking.
    
    Args:
        booking_id: Booking's unique identifier
        request: Check-in request with optional notes
        salon_id: Current salon ID from auth context
        current_user: Authenticated staff user context
        
    Returns:
        Updated booking with checked-in status
        
    Raises:
        HTTPException: 404 if booking not found, 400 if invalid status
    """
    try:
        booking_model = BookingModel()
        
        # Verify booking exists and belongs to salon
        existing = await verify_booking_access(booking_id, salon_id)
        
        # Check if booking can be checked in
        if existing.status != BookingStatus.CONFIRMED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": f"Cannot check in booking with status: {existing.status.value}", "code": "invalid_status"},
            )
        
        # Update status
        status_update = BookingStatusUpdate(
            status=BookingStatus.CHECKED_IN,
            notes=request.notes,
        )
        updated = await booking_model.update_status(booking_id, status_update)
        
        logger.info(
            "Customer checked in",
            booking_id=booking_id,
            checked_in_by=current_user.uid,
        )
        
        return updated
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to check in", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Failed to check in customer", "code": "internal_error"},
        )


@router.post(
    "/{booking_id}/start",
    response_model=Booking,
    summary="Start service",
    description="Mark service as started.",
)
async def start_service(
    booking_id: str,
    request: StartServiceRequest,
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(require_staff),
) -> Booking:
    """Start the service for a booking.
    
    Args:
        booking_id: Booking's unique identifier
        request: Start service request with optional notes
        salon_id: Current salon ID from auth context
        current_user: Authenticated staff user context
        
    Returns:
        Updated booking with in-progress status
        
    Raises:
        HTTPException: 404 if booking not found, 400 if invalid status
    """
    try:
        booking_model = BookingModel()
        
        # Verify booking exists and belongs to salon
        existing = await verify_booking_access(booking_id, salon_id)
        
        # Check if booking can be started
        if existing.status not in [BookingStatus.CONFIRMED, BookingStatus.CHECKED_IN]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": f"Cannot start booking with status: {existing.status.value}", "code": "invalid_status"},
            )
        
        # Update status
        status_update = BookingStatusUpdate(
            status=BookingStatus.IN_PROGRESS,
            notes=request.notes,
        )
        updated = await booking_model.update_status(booking_id, status_update)
        
        logger.info(
            "Service started",
            booking_id=booking_id,
            started_by=current_user.uid,
        )
        
        return updated
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to start service", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Failed to start service", "code": "internal_error"},
        )


@router.post(
    "/{booking_id}/complete",
    response_model=Booking,
    summary="Complete service",
    description="Mark service as completed.",
)
async def complete_service(
    booking_id: str,
    request: CompleteServiceRequest,
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(require_staff),
) -> Booking:
    """Complete the service for a booking.
    
    Args:
        booking_id: Booking's unique identifier
        request: Complete service request with optional feedback
        salon_id: Current salon ID from auth context
        current_user: Authenticated staff user context
        
    Returns:
        Updated booking with completed status
        
    Raises:
        HTTPException: 404 if booking not found, 400 if invalid status
    """
    try:
        booking_model = BookingModel()
        
        # Verify booking exists and belongs to salon
        existing = await verify_booking_access(booking_id, salon_id)
        
        # Check if booking can be completed
        if existing.status != BookingStatus.IN_PROGRESS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": f"Cannot complete booking with status: {existing.status.value}", "code": "invalid_status"},
            )
        
        # Update status
        status_update = BookingStatusUpdate(
            status=BookingStatus.COMPLETED,
            notes=request.notes,
        )
        updated = await booking_model.update_status(booking_id, status_update)
        
        # Update feedback if provided
        if request.rating or request.customer_feedback:
            await booking_model.update(booking_id, BookingUpdate(
                customer_feedback=request.customer_feedback,
                rating=request.rating,
            ))
        
        logger.info(
            "Service completed",
            booking_id=booking_id,
            completed_by=current_user.uid,
            rating=request.rating,
        )
        
        return updated
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to complete service", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Failed to complete service", "code": "internal_error"},
        )


@router.post(
    "/{booking_id}/upsell",
    response_model=Booking,
    summary="Add upsell service",
    description="Add an additional service to an existing booking.",
)
async def add_upsell_service(
    booking_id: str,
    request: UpsellRequest,
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(require_staff),
) -> Booking:
    """Add an upsell service to a booking.
    
    Args:
        booking_id: Booking's unique identifier
        request: Upsell request with service ID
        salon_id: Current salon ID from auth context
        current_user: Authenticated staff user context
        
    Returns:
        Updated booking with upsell added
        
    Raises:
        HTTPException: 404 if booking or service not found
    """
    try:
        booking_model = BookingModel()
        service_model = ServiceModel()
        
        # Verify booking exists and belongs to salon
        existing = await verify_booking_access(booking_id, salon_id)
        
        # Verify service exists
        service = await service_model.get(request.service_id)
        if not service or service.salon_id != salon_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": "Service not found", "code": "service_not_found"},
            )
        
        # Add upsell to booking
        updated = await booking_model.add_upsell(
            booking_id=booking_id,
            service_id=request.service_id,
            staff_id=request.staff_id,
            notes=request.notes,
        )
        
        logger.info(
            "Upsell added",
            booking_id=booking_id,
            service_id=request.service_id,
            added_by=current_user.uid,
        )
        
        return updated
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to add upsell", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Failed to add upsell service", "code": "internal_error"},
        )


__all__ = [
    "router",
    "CheckInRequest",
    "StartServiceRequest",
    "CompleteServiceRequest",
    "UpsellRequest",
    "AvailabilityRequest",
    "AvailabilityResponse",
    "SlotsResponse",
]
