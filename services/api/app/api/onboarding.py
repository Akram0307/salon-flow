"""Salon Onboarding API endpoints.

This module provides onboarding endpoints for the Salon Flow API including:
- Create new salon with owner
- Join existing salon with invite code
- Get onboarding status
- Complete onboarding steps
- Generate and validate invite codes
"""

# Standard library imports
from datetime import datetime, timedelta
from typing import Optional
import secrets
import string
import uuid

# Third-party imports
import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

# Local imports
from app.core.auth import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
)
from app.core.config import settings
from app.schemas import StaffRole, Salon, SalonCreate
from app.schemas.onboarding import (
    OnboardingStep,
    OnboardingStatus,
    OnboardingProgress,
    OnboardingState,
    OnboardingResponse,
    SalonCreateRequest,
    LayoutConfigRequest,
    BusinessHoursRequest,
    ServiceImportRequest,
    StaffInviteRequest,
    JoinSalonRequest,
    InviteCodeInfo,
)
from app.models.salon import SalonModel
from app.models.staff import StaffModel
from app.models.service import ServiceModel
from app.api.dependencies import (
    AuthContext,
    get_current_user,
    require_owner,
)
from app.data.service_templates import SERVICE_TEMPLATES, get_all_services, get_services_by_category

logger = structlog.get_logger()
router = APIRouter(tags=["Onboarding"])


# ============================================================================
# Helper Functions
# ============================================================================

def generate_invite_code(length: int = 8) -> str:
    """Generate a unique invite code."""
    chars = string.ascii_uppercase + string.digits
    chars = chars.replace('O', '').replace('0', '').replace('I', '').replace('L', '')
    return ''.join(secrets.choice(chars) for _ in range(length))


async def get_or_create_onboarding_state(salon_id: str) -> OnboardingState:
    """Get or create onboarding state for a salon."""
    from app.core.firebase import get_firestore_async
    
    db = get_firestore_async()
    docs = db.collection("onboarding_states").where("salon_id", "==", salon_id).limit(1).stream()
    
    async for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        return OnboardingState.model_validate(data)
    
    # Create new state
    state = OnboardingState(
        salon_id=salon_id,
        invite_code=generate_invite_code(),
        progress=OnboardingProgress(salon_id=salon_id),
    )
    
    await db.collection("onboarding_states").add(state.model_dump())
    return state


async def update_onboarding_progress(
    salon_id: str,
    step: OnboardingStep,
    completed: bool = True,
) -> OnboardingProgress:
    """Update onboarding progress for a salon."""
    from app.core.firebase import get_firestore_async
    
    db = get_firestore_async()
    state = await get_or_create_onboarding_state(salon_id)
    
    step_flags = {
        OnboardingStep.CREATE_SALON: "salon_created",
        OnboardingStep.CONFIGURE_LAYOUT: "layout_configured",
        OnboardingStep.ADD_SERVICES: "services_added",
        OnboardingStep.ADD_STAFF: "staff_added",
        OnboardingStep.SET_BUSINESS_HOURS: "business_hours_set",
    }
    
    if step in step_flags:
        setattr(state.progress, step_flags[step], completed)
        
        if completed and step.value not in state.progress.completed_steps:
            state.progress.completed_steps.append(step.value)
        elif not completed and step.value in state.progress.completed_steps:
            state.progress.completed_steps.remove(step.value)
    
    state.progress.current_step = state.progress.get_next_step() or OnboardingStep.COMPLETE
    
    if state.progress.get_completion_percentage() == 100:
        state.progress.status = OnboardingStatus.COMPLETED
        state.completed_at = datetime.utcnow()
    else:
        state.progress.status = OnboardingStatus.IN_PROGRESS
    
    state.updated_at = datetime.utcnow()
    
    await db.collection("onboarding_states").document(state.id).update(state.model_dump())
    
    return state.progress


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/create-salon", response_model=OnboardingResponse, status_code=status.HTTP_201_CREATED)
async def create_salon(
    request: SalonCreateRequest,
) -> OnboardingResponse:
    """Create a new salon with owner account.
    
    Uses custom JWT auth (not Firebase Auth) for user management.
    """
    try:
        from app.core.firebase import get_firestore_async
        
        db = get_firestore_async()
        
        # Check if salon with same phone/email already exists
        salon_model = SalonModel()
        existing = await salon_model.get_by_phone(request.phone)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": "Salon with this phone number already exists", "code": "salon_exists"}
            )
        
        # Check if owner email already exists
        users_ref = db.collection("users")
        existing_user = await users_ref.where("email", "==", request.owner_email).limit(1).get()
        if len(existing_user) > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": "Email already registered", "code": "email_exists"}
            )
        
        
        # Create salon entity
        salon_data = {
            "name": request.name,
            "phone": request.phone,
            "email": request.email,
            "address_line1": request.address_line1,
            "address_line2": request.address_line2,
            "city": request.city,
            "state": request.state,
            "pincode": request.pincode,
            "gst_number": request.gst_number,
            "pan_number": request.pan_number,
            "is_active": True,
            "subscription_plan": "free",
            "subscription_status": "trial",
        }
        
        salon = await salon_model.create(salon_data)
        
        # Generate user ID
        user_id = f"user_{uuid.uuid4().hex[:20]}"
        
        # Create user document (custom auth)
        user_doc = {
            "id": user_id,
            "uid": user_id,
            "email": request.owner_email,
            "phone": request.owner_phone,
            "display_name": request.owner_name,
            "name": request.owner_name,
            "password_hash": get_password_hash(request.owner_password),
            "role": "owner",
            "salon_id": salon.id,
            "is_active": True,
            "email_verified": True,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        
        await db.collection("users").document(user_id).set(user_doc)
        
        # Create staff profile for owner
        staff_model = StaffModel()
        staff_data = {
            "salon_id": salon.id,
            "name": request.owner_name,
            "phone": request.owner_phone,
            "email": request.owner_email,
            "role": StaffRole.OWNER.value,
            "user_id": user_id,
            "is_active": True,
        }
        await staff_model.create(staff_data)
        
        # Update salon with owner_id
        await salon_model.update(salon.id, {"owner_id": user_id})
        
        # Create onboarding state
        state = await get_or_create_onboarding_state(salon.id)
        await update_onboarding_progress(salon.id, OnboardingStep.CREATE_SALON)
        
        # Generate tokens
        access_token = create_access_token(
            data={
                "sub": user_id,
                "email": request.owner_email,
                "phone": request.owner_phone,
                "role": "owner",
                "salon_id": salon.id,
                "name": request.owner_name,
            }
        )
        refresh_token = create_refresh_token(
            data={"sub": user_id, "type": "refresh"}
        )
        
        logger.info(
            "Salon created successfully",
            salon_id=salon.id,
            owner_id=user_id,
        )
        
        return OnboardingResponse(
            success=True,
            message="Salon created successfully",
            salon_id=salon.id,
            invite_code=state.invite_code,
            progress=state.progress,
            next_step=OnboardingStep.CONFIGURE_LAYOUT.value,
            completion_percentage=state.progress.get_completion_percentage(),
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create salon", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"Failed to create salon: {str(e)}", "code": "creation_failed"}
        )


@router.post("/join-salon", response_model=OnboardingResponse, status_code=status.HTTP_201_CREATED)
async def join_salon(
    request: JoinSalonRequest,
) -> OnboardingResponse:
    """Join an existing salon using invite code."""
    try:
        from app.core.firebase import get_firestore_async
        
        db = get_firestore_async()
        
        # Find salon by invite code
        states_ref = db.collection("onboarding_states")
        docs = await states_ref.where("invite_code", "==", request.invite_code.upper()).limit(1).get()
        
        if len(docs) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": "Invalid invite code", "code": "invalid_invite"}
            )
        
        state_data = docs[0].to_dict()
        salon_id = state_data["salon_id"]
        
        # Get salon info
        salon_model = SalonModel()
        salon = await salon_model.get(salon_id)
        if not salon:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": "Salon not found", "code": "salon_not_found"}
            )
        
        # Check if email already exists
        users_ref = db.collection("users")
        existing_user = await users_ref.where("email", "==", request.email).limit(1).get()
        if len(existing_user) > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": "Email already registered", "code": "email_exists"}
            )
        
        # Generate user ID
        user_id = f"user_{uuid.uuid4().hex[:20]}"
        
        # Create user document
        user_doc = {
            "id": user_id,
            "uid": user_id,
            "email": request.email,
            "phone": request.phone,
            "display_name": request.name,
            "name": request.name,
            "password_hash": get_password_hash(request.password),
            "role": "stylist",
            "salon_id": salon_id,
            "is_active": True,
            "email_verified": True,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        
        await db.collection("users").document(user_id).set(user_doc)
        
        # Create staff profile
        staff_model = StaffModel()
        staff_data = {
            "salon_id": salon_id,
            "name": request.name,
            "phone": request.phone,
            "email": request.email,
            "role": StaffRole.STYLIST.value,
            "user_id": user_id,
            "is_active": True,
        }
        await staff_model.create(staff_data)
        
        # Generate tokens
        access_token = create_access_token(
            data={
                "sub": user_id,
                "email": request.email,
                "phone": request.phone,
                "role": "stylist",
                "salon_id": salon_id,
                "name": request.name,
            }
        )
        refresh_token = create_refresh_token(
            data={"sub": user_id, "type": "refresh"}
        )
        
        return OnboardingResponse(
            success=True,
            message="Successfully joined salon",
            salon_id=salon_id,
            progress=OnboardingProgress(salon_id=salon_id),
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to join salon", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"Failed to join salon: {str(e)}", "code": "join_failed"}
        )


@router.get("/status", response_model=dict)
async def get_onboarding_status(
    current_user: AuthContext = Depends(get_current_user),
) -> dict:
    """Get onboarding status for current user."""
    try:
        salon_id = current_user.salon_id
        
        if not salon_id:
            return {
                "has_salon": False,
                "onboarding_complete": False,
                "salon": None,
                "progress": None,
            }
        
        
        # Get salon info
        salon_model = SalonModel()
        salon = await salon_model.get(salon_id)
        
        # Get onboarding state
        state = await get_or_create_onboarding_state(salon_id)
        
        return {
            "has_salon": True,
            "onboarding_complete": state.progress.status == OnboardingStatus.COMPLETED,
            "salon": salon.model_dump() if salon else None,
            "progress": state.progress.model_dump(),
            "invite_code": state.invite_code,
        }
        
    except Exception as e:
        logger.error("Failed to get onboarding status", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": str(e), "code": "status_error"}
        )


@router.post("/complete", response_model=OnboardingResponse)
async def complete_onboarding(
    current_user: AuthContext = Depends(get_current_user),
) -> OnboardingResponse:
    """Mark onboarding as complete."""
    try:
        if not current_user.salon_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"message": "User not associated with any salon", "code": "no_salon"}
            )
        
        # Update all steps as complete
        for step in [
            OnboardingStep.CREATE_SALON,
            OnboardingStep.CONFIGURE_LAYOUT,
            OnboardingStep.ADD_SERVICES,
            OnboardingStep.ADD_STAFF,
            OnboardingStep.SET_BUSINESS_HOURS,
        ]:
            await update_onboarding_progress(current_user.salon_id, step)
        
        
        state = await get_or_create_onboarding_state(current_user.salon_id)
        
        return OnboardingResponse(
            success=True,
            message="Onboarding completed successfully",
            salon_id=current_user.salon_id,
            progress=state.progress,
            completion_percentage=100,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to complete onboarding", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": str(e), "code": "complete_error"}
        )


@router.post("/configure-layout", response_model=OnboardingResponse)
async def configure_layout(
    request: LayoutConfigRequest,
    current_user: AuthContext = Depends(get_current_user),
) -> OnboardingResponse:
    """Configure salon layout."""
    try:
        if not current_user.salon_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"message": "User not associated with any salon", "code": "no_salon"}
            )
        
        
        from app.core.firebase import get_firestore_async
        from app.models.resource import ResourceModel
        
        db = get_firestore_async()
        resource_model = ResourceModel()
        
        # Create men's chairs
        for i in range(request.mens_chairs):
            await resource_model.create({
                "salon_id": current_user.salon_id,
                "name": f"Men's Chair {i+1}",
                "resource_type": "chair_mens",
                "is_active": True,
            })
        
        
        # Create women's chairs
        for i in range(request.womens_chairs):
            await resource_model.create({
                "salon_id": current_user.salon_id,
                "name": f"Women's Chair {i+1}",
                "resource_type": "chair_womens",
                "is_active": True,
            })
        
        
        # Create service rooms
        for i in range(request.service_rooms):
            await resource_model.create({
                "salon_id": current_user.salon_id,
                "name": f"Service Room {i+1}",
                "resource_type": "room_treatment",
                "is_active": True,
            })
        
        
        # Create bridal room if requested
        if request.bridal_room:
            await resource_model.create({
                "salon_id": current_user.salon_id,
                "name": "Bridal Room",
                "resource_type": "room_bridal",
                "is_active": True,
            })
        
        
        # Create spa rooms
        for i in range(request.spa_rooms):
            await resource_model.create({
                "salon_id": current_user.salon_id,
                "name": f"Spa Room {i+1}",
                "resource_type": "room_spa",
                "is_active": True,
            })
        
        
        # Update progress
        progress = await update_onboarding_progress(current_user.salon_id, OnboardingStep.CONFIGURE_LAYOUT)
        
        return OnboardingResponse(
            success=True,
            message="Layout configured successfully",
            salon_id=current_user.salon_id,
            progress=progress,
            next_step=OnboardingStep.ADD_SERVICES.value,
            completion_percentage=progress.get_completion_percentage(),
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to configure layout", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": str(e), "code": "layout_error"}
        )


@router.post("/import-services", response_model=OnboardingResponse)
async def import_services(
    request: ServiceImportRequest,
    current_user: AuthContext = Depends(get_current_user),
) -> OnboardingResponse:
    """Import services from comprehensive template library.
    
    Imports 75+ service templates across 8 categories:
    - hair_cuts: 16 services
    - hair_color: 10 services
    - hair_treatments: 8 services
    - styling: 6 services
    - facial_skin: 10 services
    - spa: 16 services
    - bridal: 6 services
    - groom: 3 services
    
    Optionally filter by specific categories via request.categories.
    """
    try:
        if not current_user.salon_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"message": "User not associated with any salon", "code": "no_salon"}
            )
        
        from app.core.firebase import get_firestore_async
        
        db = get_firestore_async()
        service_model = ServiceModel()
        
        # Get services to import based on category filter
        if request.categories and len(request.categories) > 0:
            # Import only selected categories
            services_to_import = []
            for category in request.categories:
                services_to_import.extend(get_services_by_category(category))
        else:
            # Import all services
            services_to_import = get_all_services()
        
        count = 0
        imported_categories = set()
        
        for service in services_to_import:
            # Map template to Service schema with proper nested objects
            service_data = {
                "service_id": service["service_id"],
                "salon_id": current_user.salon_id,
                "name": service["name"],
                "category": service["category"],
                "description": service.get("description", ""),
                "pricing": service["pricing"],
                "duration": service["duration"],
                "resource_requirement": service.get("resource_requirement", {
                    "resource_type": "any",
                    "is_exclusive": False,
                }),
                "is_active": True,
                "is_popular": service.get("is_popular", False),
                "is_featured": service.get("is_featured", False),
                "gst_rate": service.get("gst_rate", 0.05),
            }
            await service_model.create(service_data)
            imported_categories.add(service["category"])
            count += 1
        
        # Update progress
        progress = await update_onboarding_progress(current_user.salon_id, OnboardingStep.ADD_SERVICES)
        progress.services_count = count
        
        logger.info(
            "Services imported during onboarding",
            salon_id=current_user.salon_id,
            services_count=count,
            categories=list(imported_categories),
        )
        
        return OnboardingResponse(
            success=True,
            message=f"Imported {count} services across {len(imported_categories)} categories",
            salon_id=current_user.salon_id,
            progress=progress,
            next_step=OnboardingStep.ADD_STAFF.value,
            completion_percentage=progress.get_completion_percentage(),
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to import services", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": str(e), "code": "services_error"}
        )


@router.get("/validate-invite/{invite_code}", response_model=InviteCodeInfo)
async def validate_invite_code(
    invite_code: str,
) -> InviteCodeInfo:
    """Validate an invite code and return salon info."""
    try:
        from app.core.firebase import get_firestore_async
        
        db = get_firestore_async()
        
        states_ref = db.collection("onboarding_states")
        docs = await states_ref.where("invite_code", "==", invite_code.upper()).limit(1).get()
        
        if len(docs) == 0:
            return InviteCodeInfo(
                invite_code=invite_code,
                salon_id="",
                salon_name="",
                salon_city="",
                is_valid=False,
            )
        
        state_data = docs[0].to_dict()
        salon_id = state_data["salon_id"]
        
        # Get salon info
        salon_model = SalonModel()
        salon = await salon_model.get(salon_id)
        
        return InviteCodeInfo(
            invite_code=invite_code,
            salon_id=salon_id,
            salon_name=salon.name if salon else "Unknown",
            salon_city=salon.city if salon else "Unknown",
            is_valid=True,
        )
        
    except Exception as e:
        logger.error("Failed to validate invite code", error=str(e))
        return InviteCodeInfo(
            invite_code=invite_code,
            salon_id="",
            salon_name="",
            salon_city="",
            is_valid=False,
        )

@router.get("/service-templates")
async def get_service_templates():
    """Get all service templates organized by category.
    
    Returns 75+ service templates across 8 categories for onboarding.
    """
    from app.data.service_templates import get_service_count, get_total_service_count
    
    return {
        "total_count": get_total_service_count(),
        "categories": get_service_count(),
        "templates": SERVICE_TEMPLATES,
    }



@router.post("/staff", response_model=OnboardingResponse, status_code=status.HTTP_201_CREATED)
async def add_staff(
    request: StaffInviteRequest,
    current_user: AuthContext = Depends(get_current_user),
) -> OnboardingResponse:
    """Add a staff member during onboarding.

    Creates a staff profile linked to the current user's salon with
    specified role, specializations, and availability schedule.
    """
    try:
        if not current_user.salon_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"message": "User not associated with any salon", "code": "no_salon"}
            )

        from app.core.firebase import get_firestore_async

        db = get_firestore_async()
        staff_model = StaffModel()

        # Check if staff with same phone already exists in salon
        existing_staff = await staff_model.get_by_phone(request.phone, current_user.salon_id)
        if existing_staff:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": "Staff with this phone number already exists", "code": "staff_exists"}
            )

        # Create staff profile
        # Note: specializations is a list of service names/IDs
        # We store them directly and skills can be populated later when services are assigned
        staff_data = {
            "salon_id": current_user.salon_id,
            "name": request.name,
            "phone": request.phone,
            "email": request.email,
            "role": request.role.value if hasattr(request.role, 'value') else request.role,
            "skills": {"skills": []},  # Empty skills list - can be populated later
            "is_active": True,
            "is_available": True,
            "status": "active",
        }

        staff = await staff_model.create(staff_data)

        logger.info(
            "Staff created during onboarding",
            staff_id=staff.id,
            salon_id=current_user.salon_id,
            role=request.role,
        )

        # Update onboarding progress
        progress = await update_onboarding_progress(current_user.salon_id, OnboardingStep.ADD_STAFF)

        # Get current staff count
        staff_count = await staff_model.get_active_staff_count(current_user.salon_id)
        progress.staff_count = staff_count

        return OnboardingResponse(
            success=True,
            message=f"Staff member {request.name} added successfully",
            salon_id=current_user.salon_id,
            progress=progress,
            next_step=OnboardingStep.SET_BUSINESS_HOURS.value,
            completion_percentage=progress.get_completion_percentage(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to add staff", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"Failed to add staff: {str(e)}", "code": "staff_error"}
        )


@router.post("/business-hours", response_model=OnboardingResponse)
async def set_business_hours(
    request: BusinessHoursRequest,
    current_user: AuthContext = Depends(get_current_user),
) -> OnboardingResponse:
    """Set salon business hours during onboarding.

    Updates salon operating hours for each day of the week.
    Stores in Firestore under the salon document.
    """
    try:
        if not current_user.salon_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"message": "User not associated with any salon", "code": "no_salon"}
            )

        from app.core.firebase import get_firestore_async

        db = get_firestore_async()
        salon_model = SalonModel()

        # Get current salon
        salon = await salon_model.get(current_user.salon_id)
        if not salon:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": "Salon not found", "code": "salon_not_found"}
            )

        # Convert request to OperatingHours
        operating_hours = request.to_operating_hours()

        # Update salon with operating hours
        operating_hours_dict = operating_hours.model_dump()

        # Convert time objects to ISO format strings for Firestore
        for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
            day_hours = operating_hours_dict.get(day, {})
            if day_hours.get('open_time'):
                day_hours['open_time'] = day_hours['open_time'].isoformat() if hasattr(day_hours['open_time'], 'isoformat') else day_hours['open_time']
            if day_hours.get('close_time'):
                day_hours['close_time'] = day_hours['close_time'].isoformat() if hasattr(day_hours['close_time'], 'isoformat') else day_hours['close_time']
            if day_hours.get('break_start'):
                day_hours['break_start'] = day_hours['break_start'].isoformat() if hasattr(day_hours['break_start'], 'isoformat') else day_hours['break_start']
            if day_hours.get('break_end'):
                day_hours['break_end'] = day_hours['break_end'].isoformat() if hasattr(day_hours['break_end'], 'isoformat') else day_hours['break_end']
            operating_hours_dict[day] = day_hours

        await salon_model.update(current_user.salon_id, {
            "operating_hours": operating_hours_dict
        })

        logger.info(
            "Business hours set during onboarding",
            salon_id=current_user.salon_id,
        )

        # Update onboarding progress
        progress = await update_onboarding_progress(current_user.salon_id, OnboardingStep.SET_BUSINESS_HOURS)

        return OnboardingResponse(
            success=True,
            message="Business hours set successfully",
            salon_id=current_user.salon_id,
            progress=progress,
            next_step=OnboardingStep.COMPLETE.value,
            completion_percentage=progress.get_completion_percentage(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to set business hours", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"Failed to set business hours: {str(e)}", "code": "hours_error"}
        )
