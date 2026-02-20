"""Resource Management Routes for Salon Flow API.

Handles resource operations including:
- Resource CRUD operations
- Resource availability checking
- Resource booking management
"""
from datetime import datetime, date, time
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
from app.models import ResourceModel, BookingModel
from app.schemas import (
    ResourceCreate,
    ResourceUpdate,
    Resource,
    ResourceSummary,
    ResourceType,
    ResourceStatus,
    PaginatedResponse,
)

logger = structlog.get_logger()
router = APIRouter(tags=["Resource Management"])


# ============================================================================
# Request/Response Schemas
# ============================================================================

class ResourceAvailabilitySlot(BaseModel):
    """Resource availability slot."""
    start_time: time
    end_time: time
    available: bool
    booking_id: Optional[str] = None


class ResourceAvailabilityResponse(BaseModel):
    """Resource availability response."""
    resource_id: str
    resource_name: str
    date: date
    slots: List[ResourceAvailabilitySlot]
    total_slots: int
    available_slots: int


# ============================================================================
# Routes
# ============================================================================

@router.get(
    "/",
    response_model=PaginatedResponse[ResourceSummary],
    summary="List resources",
    description="List all resources with pagination and filtering.",
)
async def list_resources(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    resource_type: Optional[ResourceType] = Query(None, description="Filter by type"),
    status_filter: Optional[ResourceStatus] = Query(None, alias="status", description="Filter by status"),
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(get_current_user),
):
    """List resources with pagination and filtering."""
    try:
        resource_model = ResourceModel()
        
        result = await resource_model.search(
            salon_id=salon_id,
            resource_type=resource_type,
            status=status_filter,
            page=page,
            page_size=page_size,
        )
        
        return result
        
    except Exception as e:
        logger.error("Failed to list resources", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve resources",
        )


@router.post(
    "/",
    response_model=Resource,
    status_code=status.HTTP_201_CREATED,
    summary="Create resource",
    description="Create a new resource (chair, room, equipment).",
)
async def create_resource(
    request: ResourceCreate,
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(require_manager),
):
    """Create a new resource.
    
    Only managers and owners can create resources.
    """
    try:
        resource_model = ResourceModel()
        
        # Check for existing resource with same name
        existing = await resource_model.find_by_name(request.name, salon_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Resource with this name already exists",
            )
        
        # Set salon_id from context
        resource_data = request.model_copy(update={
            "salon_id": salon_id,
        })
        
        resource = await resource_model.create(resource_data)
        
        logger.info(
            "Resource created",
            resource_id=resource.id,
            salon_id=salon_id,
            resource_type=request.resource_type,
            created_by=current_user.uid,
        )
        
        return resource
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create resource", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create resource",
        )


@router.get(
    "/availability",
    response_model=List[ResourceAvailabilityResponse],
    summary="Get resource availability",
    description="Get availability for all resources or specific type on a date.",
)
async def get_resource_availability(
    date_param: date = Query(..., alias="date", description="Date to check"),
    resource_type: Optional[ResourceType] = Query(None, description="Filter by type"),
    resource_id: Optional[str] = Query(None, description="Specific resource ID"),
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(get_current_user),
):
    """Get resource availability for a specific date."""
    try:
        resource_model = ResourceModel()
        booking_model = BookingModel()
        
        # Get resources
        if resource_id:
            resources = [await resource_model.get(resource_id)]
            if not resources[0] or resources[0].salon_id != salon_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Resource not found",
                )
        else:
            resources = await resource_model.get_all(
                salon_id=salon_id,
                resource_type=resource_type,
                status=ResourceStatus.AVAILABLE,
            )
        
        result = []
        for resource in resources:
            if not resource:
                continue
                
            # Get bookings for this resource on this date
            bookings = await booking_model.get_by_resource(
                resource_id=resource.id,
                date=date_param,
            )
            
            # Generate availability slots (30-minute intervals)
            slots = []
            start_hour = 9  # 9 AM
            end_hour = 21   # 9 PM
            
            for hour in range(start_hour, end_hour):
                for minute in [0, 30]:
                    slot_start = time(hour, minute)
                    slot_end = time(
                        hour + 1 if minute == 30 else hour,
                        0 if minute == 30 else 30
                    )
                    
                    # Check if slot is booked
                    is_available = True
                    booking_id = None
                    
                    for booking in bookings:
                        booking_start = booking.start_time.time()
                        booking_end = booking.end_time.time()
                        
                        if slot_start < booking_end and slot_end > booking_start:
                            is_available = False
                            booking_id = booking.id
                            break
                    
                    slots.append(ResourceAvailabilitySlot(
                        start_time=slot_start,
                        end_time=slot_end,
                        available=is_available,
                        booking_id=booking_id,
                    ))
            
            available_count = sum(1 for s in slots if s.available)
            
            result.append(ResourceAvailabilityResponse(
                resource_id=resource.id,
                resource_name=resource.name,
                date=date_param,
                slots=slots,
                total_slots=len(slots),
                available_slots=available_count,
            ))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get availability", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve availability",
        )


@router.get(
    "/{resource_id}",
    response_model=Resource,
    summary="Get resource",
    description="Get detailed resource information.",
)
async def get_resource(
    resource_id: str,
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(get_current_user),
):
    """Get resource by ID."""
    try:
        resource_model = ResourceModel()
        resource = await resource_model.get(resource_id)
        
        if not resource:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resource not found",
            )
        
        # Verify salon access
        if resource.salon_id != salon_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )
        
        return resource
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get resource", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve resource",
        )


@router.put(
    "/{resource_id}",
    response_model=Resource,
    summary="Update resource",
    description="Update resource information.",
)
async def update_resource(
    resource_id: str,
    request: ResourceUpdate,
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(require_manager),
):
    """Update resource.
    
    Managers and owners can update resources.
    """
    try:
        resource_model = ResourceModel()
        
        # Verify resource exists and belongs to salon
        existing = await resource_model.get(resource_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resource not found",
            )
        
        if existing.salon_id != salon_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )
        
        # Update resource
        updated = await resource_model.update(resource_id, request)
        
        logger.info(
            "Resource updated",
            resource_id=resource_id,
            updated_by=current_user.uid,
        )
        
        return updated
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update resource", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update resource",
        )
