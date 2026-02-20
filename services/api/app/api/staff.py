"""Staff Management Routes for Salon Flow API.

Handles staff operations including:
- Staff CRUD operations
- Availability management
- Skills and expertise
- Shift tracking
- Booking assignments
"""
from datetime import datetime, date
from typing import Optional, List, Dict

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
from app.models import StaffModel, BookingModel, ShiftModel
from app.schemas import (
    StaffCreate,
    StaffUpdate,
    Staff,
    StaffSummary,
    StaffSearch,
    StaffSkill,
    StaffAvailability,
    StaffRole,
    StaffStatus,
    BookingSummary,
    PaginatedResponse,
)

logger = structlog.get_logger()
router = APIRouter(prefix="/staff", tags=["Staff Management"])


# ============================================================================
# Request/Response Schemas
# ============================================================================

class AvailabilityUpdateRequest(BaseModel):
    """Staff availability update request."""
    monday: Optional[Dict] = None
    tuesday: Optional[Dict] = None
    wednesday: Optional[Dict] = None
    thursday: Optional[Dict] = None
    friday: Optional[Dict] = None
    saturday: Optional[Dict] = None
    sunday: Optional[Dict] = None


class SkillsUpdateRequest(BaseModel):
    """Staff skills update request."""
    skills: List[StaffSkill]


class AvailabilityResponse(BaseModel):
    """Staff availability response."""
    staff_id: str
    availability: Dict[str, Dict]
    timezone: str


class SkillsResponse(BaseModel):
    """Staff skills response."""
    staff_id: str
    skills: List[StaffSkill]
    total_services: int
    expertise_level: str


# ============================================================================
# Routes
# ============================================================================

@router.get(
    "",
    response_model=PaginatedResponse[StaffSummary],
    summary="List staff",
    description="List all staff members with pagination and filtering.",
)
async def list_staff(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    role: Optional[StaffRole] = Query(None, description="Filter by role"),
    status_filter: Optional[StaffStatus] = Query(None, alias="status", description="Filter by status"),
    search: Optional[str] = Query(None, description="Search by name"),
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(get_current_user),
):
    """List staff members with pagination and filtering."""
    try:
        staff_model = StaffModel()
        
        # Build search query
        query = StaffSearch(
            salon_id=salon_id,
            role=role,
            status=status_filter,
            search=search,
        )
        
        result = await staff_model.search(
            query=query,
            page=page,
            page_size=page_size,
        )
        
        return result
        
    except Exception as e:
        logger.error("Failed to list staff", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve staff",
        )


@router.post(
    "",
    response_model=Staff,
    status_code=status.HTTP_201_CREATED,
    summary="Create staff",
    description="Create a new staff member.",
)
async def create_staff(
    request: StaffCreate,
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(require_manager),
):
    """Create a new staff member.
    
    Only managers and owners can create staff.
    """
    try:
        staff_model = StaffModel()
        
        # Check for existing staff with same email
        if request.email:
            existing = await staff_model.find_by_email(request.email, salon_id)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Staff with this email already exists",
                )
        
        # Set salon_id from context
        staff_data = request.model_copy(update={
            "salon_id": salon_id,
        })
        
        staff = await staff_model.create(staff_data)
        
        logger.info(
            "Staff created",
            staff_id=staff.id,
            salon_id=salon_id,
            created_by=current_user.uid,
        )
        
        return staff
        
    except HTTPException:
        raise
    except ValueError as e:
        # Handle validation errors from model (e.g., duplicate phone)
        logger.warning("Staff validation error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error("Failed to create staff", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create staff",
        )


@router.get(
    "/{staff_id}",
    response_model=Staff,
    summary="Get staff",
    description="Get detailed staff information.",
)
async def get_staff(
    staff_id: str,
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(get_current_user),
):
    """Get staff member by ID."""
    try:
        staff_model = StaffModel()
        staff = await staff_model.get(staff_id)
        
        if not staff:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Staff not found",
            )
        
        # Verify salon access
        if staff.salon_id != salon_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )
        
        return staff
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get staff", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve staff",
        )


@router.put(
    "/{staff_id}",
    response_model=Staff,
    summary="Update staff",
    description="Update staff information.",
)
async def update_staff(
    staff_id: str,
    request: StaffUpdate,
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(require_manager),
):
    """Update staff member.
    
    Managers and owners can update staff.
    """
    try:
        staff_model = StaffModel()
        
        # Verify staff exists and belongs to salon
        existing = await staff_model.get(staff_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Staff not found",
            )
        
        if existing.salon_id != salon_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )
        
        # Update staff
        updated = await staff_model.update(staff_id, request)
        
        logger.info(
            "Staff updated",
            staff_id=staff_id,
            updated_by=current_user.uid,
        )
        
        return updated
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update staff", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update staff",
        )


@router.delete(
    "/{staff_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete staff",
    description="Soft delete a staff member (mark as inactive).",
)
async def delete_staff(
    staff_id: str,
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(require_manager),
):
    """Soft delete staff by marking as inactive."""
    try:
        staff_model = StaffModel()
        
        # Verify staff exists and belongs to salon
        existing = await staff_model.get(staff_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Staff not found",
            )
        
        if existing.salon_id != salon_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )
        
        # Soft delete
        await staff_model.soft_delete(staff_id)
        
        logger.info(
            "Staff deleted",
            staff_id=staff_id,
            deleted_by=current_user.uid,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete staff", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete staff",
        )


@router.get(
    "/{staff_id}/availability",
    response_model=AvailabilityResponse,
    summary="Get staff availability",
    description="Get staff member's weekly availability schedule.",
)
async def get_staff_availability(
    staff_id: str,
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(get_current_user),
):
    """Get staff availability schedule."""
    try:
        staff_model = StaffModel()
        staff = await staff_model.get(staff_id)
        
        if not staff or staff.salon_id != salon_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Staff not found",
            )
        
        return AvailabilityResponse(
            staff_id=staff_id,
            availability=staff.availability.model_dump() if staff.availability else {},
            timezone="Asia/Kolkata",
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get availability", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve availability",
        )


@router.put(
    "/{staff_id}/availability",
    response_model=AvailabilityResponse,
    summary="Update staff availability",
    description="Update staff member's weekly availability schedule.",
)
async def update_staff_availability(
    staff_id: str,
    request: AvailabilityUpdateRequest,
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(require_manager),
):
    """Update staff availability.
    
    Managers and owners can update availability.
    """
    try:
        staff_model = StaffModel()
        
        # Verify staff exists and belongs to salon
        existing = await staff_model.get(staff_id)
        if not existing or existing.salon_id != salon_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Staff not found",
            )
        
        # Build availability dict
        availability_data = request.model_dump(exclude_unset=True)
        
        # Update staff
        update_data = StaffUpdate(availability=availability_data)
        await staff_model.update(staff_id, update_data)
        
        logger.info(
            "Staff availability updated",
            staff_id=staff_id,
        )
        
        return AvailabilityResponse(
            staff_id=staff_id,
            availability=availability_data,
            timezone="Asia/Kolkata",
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update availability", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update availability",
        )


@router.get(
    "/{staff_id}/skills",
    response_model=SkillsResponse,
    summary="Get staff skills",
    description="Get staff member's skills and service expertise.",
)
async def get_staff_skills(
    staff_id: str,
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(get_current_user),
):
    """Get staff skills and expertise."""
    try:
        staff_model = StaffModel()
        staff = await staff_model.get(staff_id)
        
        if not staff or staff.salon_id != salon_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Staff not found",
            )
        
        skills = staff.skills or []
        
        return SkillsResponse(
            staff_id=staff_id,
            skills=skills,
            total_services=len(skills),
            expertise_level=staff.expertise_level.value if staff.expertise_level else "junior",
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get skills", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve skills",
        )


@router.put(
    "/{staff_id}/skills",
    response_model=SkillsResponse,
    summary="Update staff skills",
    description="Update staff member's skills and service expertise.",
)
async def update_staff_skills(
    staff_id: str,
    request: SkillsUpdateRequest,
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(require_manager),
):
    """Update staff skills.
    
    Managers and owners can update skills.
    """
    try:
        staff_model = StaffModel()
        
        # Verify staff exists and belongs to salon
        existing = await staff_model.get(staff_id)
        if not existing or existing.salon_id != salon_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Staff not found",
            )
        
        # Update staff
        skills_data = [s.model_dump() for s in request.skills]
        update_data = StaffUpdate(skills=skills_data)
        await staff_model.update(staff_id, update_data)
        
        logger.info(
            "Staff skills updated",
            staff_id=staff_id,
            skills_count=len(request.skills),
        )
        
        return SkillsResponse(
            staff_id=staff_id,
            skills=request.skills,
            total_services=len(request.skills),
            expertise_level=existing.expertise_level.value if existing.expertise_level else "junior",
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update skills", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update skills",
        )


@router.get(
    "/{staff_id}/shifts",
    response_model=PaginatedResponse,
    summary="Get staff shifts",
    description="Get staff member's shift history.",
)
async def get_staff_shifts(
    staff_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(get_current_user),
):
    """Get staff shift history."""
    try:
        # Verify staff exists and belongs to salon
        staff_model = StaffModel()
        staff = await staff_model.get(staff_id)
        
        if not staff or staff.salon_id != salon_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Staff not found",
            )
        
        # Get shifts
        shift_model = ShiftModel()
        shifts = await shift_model.get_by_staff(
            staff_id=staff_id,
            salon_id=salon_id,
            start_date=start_date,
            end_date=end_date,
            page=page,
            page_size=page_size,
        )
        
        return shifts
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get shifts", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve shifts",
        )


@router.get(
    "/{staff_id}/bookings",
    response_model=PaginatedResponse[BookingSummary],
    summary="Get staff bookings",
    description="Get staff member's assigned bookings.",
)
async def get_staff_bookings(
    staff_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    date_filter: Optional[date] = Query(None, alias="date"),
    status_filter: Optional[str] = Query(None, alias="status"),
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(get_current_user),
):
    """Get staff's assigned bookings."""
    try:
        # Verify staff exists and belongs to salon
        staff_model = StaffModel()
        staff = await staff_model.get(staff_id)
        
        if not staff or staff.salon_id != salon_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Staff not found",
            )
        
        # Get bookings
        booking_model = BookingModel()
        bookings = await booking_model.get_by_staff(
            staff_id=staff_id,
            salon_id=salon_id,
            date=date_filter,
            status=status_filter,
            page=page,
            page_size=page_size,
        )
        
        return bookings
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get bookings", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve bookings",
        )
