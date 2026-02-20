"""Shift Management Routes for Salon Flow API.

Handles shift operations including:
- Shift CRUD operations
- Clock in/out management
- Leave request management
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
from app.models import ShiftModel, StaffModel
from app.schemas import (
    ShiftCreate,
    ShiftUpdate,
    Shift,
    ShiftSummary,
    ShiftStatus,
    LeaveRequestCreate,
    LeaveRequestUpdate,
    LeaveRequest,
    LeaveRequestStatus,
    LeaveType,
    PaginatedResponse,
)

logger = structlog.get_logger()
router = APIRouter(prefix="/shifts", tags=["Shift Management"])


# ============================================================================
# Request/Response Schemas
# ============================================================================

class ClockInRequest(BaseModel):
    """Clock in request."""
    notes: Optional[str] = None


class ClockOutRequest(BaseModel):
    """Clock out request."""
    notes: Optional[str] = None


class ClockResponse(BaseModel):
    """Clock in/out response."""
    shift_id: str
    staff_id: str
    action: str
    time: datetime
    notes: Optional[str]
    total_hours: Optional[float] = None


class LeaveRequestResponse(BaseModel):
    """Leave request response."""
    leave_request_id: str
    staff_id: str
    staff_name: str
    leave_type: str
    start_date: date
    end_date: date
    reason: Optional[str]
    status: str
    approved_by: Optional[str]
    approved_at: Optional[datetime]


# ============================================================================
# Routes
# ============================================================================

@router.get(
    "",
    response_model=PaginatedResponse[ShiftSummary],
    summary="List shifts",
    description="List all shifts with pagination and filtering.",
)
async def list_shifts(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    staff_id: Optional[str] = Query(None, description="Filter by staff"),
    date_filter: Optional[date] = Query(None, alias="date", description="Filter by date"),
    status_filter: Optional[ShiftStatus] = Query(None, alias="status", description="Filter by status"),
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(get_current_user),
):
    """List shifts with pagination and filtering."""
    try:
        shift_model = ShiftModel()
        
        result = await shift_model.search(
            salon_id=salon_id,
            staff_id=staff_id,
            date=date_filter,
            status=status_filter,
            page=page,
            page_size=page_size,
        )
        
        return result
        
    except Exception as e:
        logger.error("Failed to list shifts", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve shifts",
        )


@router.post(
    "",
    response_model=Shift,
    status_code=status.HTTP_201_CREATED,
    summary="Create shift",
    description="Create a new shift for a staff member.",
)
async def create_shift(
    request: ShiftCreate,
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(require_manager),
):
    """Create a new shift.
    
    Only managers and owners can create shifts.
    """
    try:
        shift_model = ShiftModel()
        staff_model = StaffModel()
        
        # Verify staff exists
        staff = await staff_model.get(request.staff_id)
        if not staff or staff.salon_id != salon_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Staff not found",
            )
        
        # Check for overlapping shifts
        overlapping = await shift_model.check_overlap(
            staff_id=request.staff_id,
            start_time=request.start_time,
            end_time=request.end_time,
        )
        
        if overlapping:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Shift overlaps with existing shift",
            )
        
        # Set salon_id from context
        shift_data = request.model_copy(update={
            "salon_id": salon_id,
            "status": ShiftStatus.SCHEDULED,
        })
        
        shift = await shift_model.create(shift_data)
        
        logger.info(
            "Shift created",
            shift_id=shift.id,
            salon_id=salon_id,
            staff_id=request.staff_id,
            created_by=current_user.uid,
        )
        
        return shift
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create shift", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create shift",
        )


@router.get(
    "/{shift_id}",
    response_model=Shift,
    summary="Get shift",
    description="Get detailed shift information.",
)
async def get_shift(
    shift_id: str,
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(get_current_user),
):
    """Get shift by ID."""
    try:
        shift_model = ShiftModel()
        shift = await shift_model.get(shift_id)
        
        if not shift:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Shift not found",
            )
        
        # Verify salon access
        if shift.salon_id != salon_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )
        
        return shift
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get shift", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve shift",
        )


@router.put(
    "/{shift_id}",
    response_model=Shift,
    summary="Update shift",
    description="Update shift information.",
)
async def update_shift(
    shift_id: str,
    request: ShiftUpdate,
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(require_manager),
):
    """Update shift.
    
    Managers and owners can update shifts.
    """
    try:
        shift_model = ShiftModel()
        
        # Verify shift exists and belongs to salon
        existing = await shift_model.get(shift_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Shift not found",
            )
        
        if existing.salon_id != salon_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )
        
        # Update shift
        updated = await shift_model.update(shift_id, request)
        
        logger.info(
            "Shift updated",
            shift_id=shift_id,
            updated_by=current_user.uid,
        )
        
        return updated
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update shift", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update shift",
        )


@router.post(
    "/{shift_id}/clock-in",
    response_model=ClockResponse,
    summary="Clock in",
    description="Clock in for a shift.",
)
async def clock_in(
    shift_id: str,
    request: ClockInRequest,
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(require_staff),
):
    """Clock in for a shift."""
    try:
        shift_model = ShiftModel()
        
        # Verify shift exists and belongs to salon
        existing = await shift_model.get(shift_id)
        if not existing or existing.salon_id != salon_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Shift not found",
            )
        
        # Check if already clocked in
        if existing.status == ShiftStatus.IN_PROGRESS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Already clocked in",
            )
        
        # Update shift
        clock_in_time = datetime.now()
        update_data = ShiftUpdate(
            status=ShiftStatus.IN_PROGRESS,
            actual_start_time=clock_in_time,
            notes=request.notes,
        )
        
        await shift_model.update(shift_id, update_data)
        
        logger.info(
            "Staff clocked in",
            shift_id=shift_id,
            staff_id=existing.staff_id,
            clock_in_time=clock_in_time,
        )
        
        return ClockResponse(
            shift_id=shift_id,
            staff_id=existing.staff_id,
            action="clock_in",
            time=clock_in_time,
            notes=request.notes,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to clock in", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clock in",
        )


@router.post(
    "/{shift_id}/clock-out",
    response_model=ClockResponse,
    summary="Clock out",
    description="Clock out from a shift.",
)
async def clock_out(
    shift_id: str,
    request: ClockOutRequest,
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(require_staff),
):
    """Clock out from a shift."""
    try:
        shift_model = ShiftModel()
        
        # Verify shift exists and belongs to salon
        existing = await shift_model.get(shift_id)
        if not existing or existing.salon_id != salon_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Shift not found",
            )
        
        # Check if clocked in
        if existing.status != ShiftStatus.IN_PROGRESS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Not clocked in",
            )
        
        # Update shift
        clock_out_time = datetime.now()
        
        # Calculate total hours
        if existing.actual_start_time:
            total_hours = (clock_out_time - existing.actual_start_time).total_seconds() / 3600
        else:
            total_hours = 0
        
        update_data = ShiftUpdate(
            status=ShiftStatus.COMPLETED,
            actual_end_time=clock_out_time,
            notes=request.notes,
        )
        
        await shift_model.update(shift_id, update_data)
        
        logger.info(
            "Staff clocked out",
            shift_id=shift_id,
            staff_id=existing.staff_id,
            clock_out_time=clock_out_time,
            total_hours=round(total_hours, 2),
        )
        
        return ClockResponse(
            shift_id=shift_id,
            staff_id=existing.staff_id,
            action="clock_out",
            time=clock_out_time,
            notes=request.notes,
            total_hours=round(total_hours, 2),
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to clock out", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clock out",
        )


# ============================================================================
# Leave Request Routes
# ============================================================================

@router.get(
    "/leave-requests",
    response_model=PaginatedResponse[LeaveRequestResponse],
    summary="Get leave requests",
    description="Get all leave requests with filtering.",
)
async def get_leave_requests(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    staff_id: Optional[str] = Query(None, description="Filter by staff"),
    status_filter: Optional[LeaveRequestStatus] = Query(None, alias="status", description="Filter by status"),
    leave_type: Optional[LeaveType] = Query(None, description="Filter by leave type"),
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(get_current_user),
):
    """Get leave requests with pagination and filtering."""
    try:
        shift_model = ShiftModel()
        staff_model = StaffModel()
        
        # Get leave requests
        leave_requests = await shift_model.get_leave_requests(
            salon_id=salon_id,
            staff_id=staff_id,
            status=status_filter,
            leave_type=leave_type,
            page=page,
            page_size=page_size,
        )
        
        # Enrich with staff names
        result = []
        for lr in leave_requests.get("items", []):
            staff = await staff_model.get(lr.staff_id)
            result.append(LeaveRequestResponse(
                leave_request_id=lr.id,
                staff_id=lr.staff_id,
                staff_name=staff.name if staff else "Unknown",
                leave_type=lr.leave_type.value,
                start_date=lr.start_date,
                end_date=lr.end_date,
                reason=lr.reason,
                status=lr.status.value,
                approved_by=lr.approved_by,
                approved_at=lr.approved_at,
            ))
        
        return PaginatedResponse(
            items=result,
            total=leave_requests.get("total", 0),
            page=page,
            page_size=page_size,
        )
        
    except Exception as e:
        logger.error("Failed to get leave requests", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve leave requests",
        )


@router.post(
    "/leave-requests",
    response_model=LeaveRequest,
    status_code=status.HTTP_201_CREATED,
    summary="Create leave request",
    description="Submit a leave request.",
)
async def create_leave_request(
    request: LeaveRequestCreate,
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(require_staff),
):
    """Create a leave request."""
    try:
        shift_model = ShiftModel()
        staff_model = StaffModel()
        
        # Verify staff exists
        staff = await staff_model.get(request.staff_id)
        if not staff or staff.salon_id != salon_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Staff not found",
            )
        
        # Create leave request
        leave_data = request.model_copy(update={
            "salon_id": salon_id,
            "status": LeaveRequestStatus.PENDING,
        })
        
        leave_request = await shift_model.create_leave_request(leave_data)
        
        logger.info(
            "Leave request created",
            leave_request_id=leave_request.id,
            staff_id=request.staff_id,
            leave_type=request.leave_type,
        )
        
        return leave_request
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create leave request", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create leave request",
        )


@router.put(
    "/leave-requests/{leave_id}/approve",
    response_model=LeaveRequest,
    summary="Approve leave request",
    description="Approve a pending leave request.",
)
async def approve_leave_request(
    leave_id: str,
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(require_manager),
):
    """Approve a leave request.
    
    Only managers and owners can approve leave requests.
    """
    try:
        shift_model = ShiftModel()
        
        # Get leave request
        leave_request = await shift_model.get_leave_request(leave_id)
        
        if not leave_request or leave_request.salon_id != salon_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Leave request not found",
            )
        
        # Check if already processed
        if leave_request.status != LeaveRequestStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Leave request already {leave_request.status.value}",
            )
        
        # Approve
        update_data = LeaveRequestUpdate(
            status=LeaveRequestStatus.APPROVED,
            approved_by=current_user.uid,
            approved_at=datetime.now(),
        )
        
        updated = await shift_model.update_leave_request(leave_id, update_data)
        
        logger.info(
            "Leave request approved",
            leave_request_id=leave_id,
            approved_by=current_user.uid,
        )
        
        return updated
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to approve leave request", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to approve leave request",
        )


@router.put(
    "/leave-requests/{leave_id}/reject",
    response_model=LeaveRequest,
    summary="Reject leave request",
    description="Reject a pending leave request.",
)
async def reject_leave_request(
    leave_id: str,
    reason: Optional[str] = Query(None, description="Rejection reason"),
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(require_manager),
):
    """Reject a leave request.
    
    Only managers and owners can reject leave requests.
    """
    try:
        shift_model = ShiftModel()
        
        # Get leave request
        leave_request = await shift_model.get_leave_request(leave_id)
        
        if not leave_request or leave_request.salon_id != salon_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Leave request not found",
            )
        
        # Check if already processed
        if leave_request.status != LeaveRequestStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Leave request already {leave_request.status.value}",
            )
        
        # Reject
        update_data = LeaveRequestUpdate(
            status=LeaveRequestStatus.REJECTED,
            approved_by=current_user.uid,
            approved_at=datetime.now(),
            rejection_reason=reason,
        )
        
        updated = await shift_model.update_leave_request(leave_id, update_data)
        
        logger.info(
            "Leave request rejected",
            leave_request_id=leave_id,
            rejected_by=current_user.uid,
            reason=reason,
        )
        
        return updated
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to reject leave request", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reject leave request",
        )
