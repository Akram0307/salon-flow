"""Staff Firestore Model.

Handles all database operations for staff member entities.
"""
from datetime import datetime, date, time
from typing import List, Optional, Dict, Any

from google.cloud.firestore_v1.base_query import FieldFilter
import structlog

from app.models.base import FirestoreBase
from app.schemas import (
    Staff,
    StaffCreate,
    StaffUpdate,
    StaffRole,
    StaffStatus,
)
from app.schemas.base import PaginatedResponse

logger = structlog.get_logger()


class StaffModel(FirestoreBase[Staff, StaffCreate, StaffUpdate]):
    """Model for staff operations.
    
    Provides CRUD operations and specialized queries for staff entities.
    Staff members belong to a salon and have roles, skills, and availability.
    
    Attributes:
        collection_name: Firestore collection name ('staff')
        model: Pydantic model for Staff
        create_schema: Pydantic schema for creating staff
        update_schema: Pydantic schema for updating staff
    
    Example:
        staff_model = StaffModel()
        stylists = await staff_model.get_by_role("stylist", salon_id="salon_123")
    """
    
    collection_name = "staff"
    model = Staff
    create_schema = StaffCreate
    update_schema = StaffUpdate
    
    async def get_by_role(
        self,
        role: str,
        salon_id: str,
        active_only: bool = True,
        limit: int = 50,
    ) -> List[Staff]:
        """Get staff members by role.
        
        Args:
            role: Staff role (owner, manager, receptionist, stylist, assistant)
            salon_id: Salon ID for multi-tenant filtering
            active_only: If True, only return active staff
            limit: Maximum results to return
            
        Returns:
            List of staff members with the specified role
        
        Example:
            stylists = await staff_model.get_by_role("stylist", salon_id="salon_123")
        """
        filters = [("role", "==", role)]
        
        if active_only:
            filters.append(("status", "==", "active"))
        
        return await self.list(
            salon_id=salon_id,
            filters=filters,
            order_by="name",
            limit=limit,
        )
    
    async def get_available_staff(
        self,
        salon_id: str,
        date: date,
        start_time: Optional[time] = None,
        end_time: Optional[time] = None,
        limit: int = 20,
    ) -> List[Staff]:
        """Get staff members available on a specific date and time.
        
        Args:
            salon_id: Salon ID for multi-tenant filtering
            date: Date to check availability
            start_time: Optional start time filter
            end_time: Optional end time filter
            limit: Maximum results to return
            
        Returns:
            List of available staff members
            
        Note:
            This returns staff who are marked as available.
            For detailed availability, check shifts collection.
        """
        filters = [
            ("status", "==", "active"),
            ("is_available", "==", True),
        ]
        
        return await self.list(
            salon_id=salon_id,
            filters=filters,
            order_by="name",
            limit=limit,
        )
    
    async def get_staff_with_skill(
        self,
        skill: str,
        salon_id: str,
        min_level: Optional[str] = None,
        limit: int = 20,
    ) -> List[Staff]:
        """Get staff members with a specific skill.
        
        Args:
            skill: Skill name to search for
            salon_id: Salon ID for multi-tenant filtering
            min_level: Minimum expertise level (beginner, intermediate, expert)
            limit: Maximum results to return
            
        Returns:
            List of staff members with the skill
        """
        try:
            # Query staff with the skill
            # Note: Skills are stored as an array of objects
            # This requires a more complex query or client-side filtering
            
            staff_list = await self.list(
                salon_id=salon_id,
                filters=[("status", "==", "active")],
                limit=limit * 2,  # Fetch more for filtering
            )
            
            # Filter by skill
            results = []
            for staff in staff_list:
                if staff.skills:
                    for s in staff.skills:
                        if s.name.lower() == skill.lower():
                            if min_level:
                                level_order = {"beginner": 1, "intermediate": 2, "expert": 3}
                                if level_order.get(s.level.value, 0) >= level_order.get(min_level, 0):
                                    results.append(staff)
                            else:
                                results.append(staff)
                            break
            
            return results[:limit]
            
        except Exception as e:
            logger.error(
                "Failed to get staff with skill",
                skill=skill,
                salon_id=salon_id,
                error=str(e),
            )
            raise
    
    async def get_by_name(
        self,
        name: str,
        salon_id: str,
        limit: int = 10,
    ) -> List[Staff]:
        """Search staff by name.
        
        Args:
            name: Name prefix to search
            salon_id: Salon ID for multi-tenant filtering
            limit: Maximum results to return
            
        Returns:
            List of matching staff members
        """
        return await self.search("name", name, salon_id=salon_id, limit=limit)
    
    async def get_by_phone(
        self,
        phone: str,
        salon_id: str,
    ) -> Optional[Staff]:
        """Get staff member by phone number.
        
        Args:
            phone: Phone number
            salon_id: Salon ID for multi-tenant filtering
            
        Returns:
            Staff member if found, None otherwise
        """
        return await self.get_by_field("phone", phone, salon_id=salon_id)
    
    async def get_by_email(
        self,
        email: str,
        salon_id: str,
    ) -> Optional[Staff]:
        """Get staff member by email.
        
        Args:
            email: Email address
            salon_id: Salon ID for multi-tenant filtering
            
        Returns:
            Staff member if found, None otherwise
        """
        return await self.get_by_field("email", email, salon_id=salon_id)
    
    async def get_by_auth_id(
        self,
        auth_id: str,
    ) -> Optional[Staff]:
        """Get staff member by Firebase Auth ID.
        
        Args:
            auth_id: Firebase Auth UID
            
        Returns:
            Staff member if found, None otherwise
        """
        return await self.get_by_field("auth_id", auth_id)
    
    async def get_stylists(
        self,
        salon_id: str,
        active_only: bool = True,
        limit: int = 50,
    ) -> List[Staff]:
        """Get all stylists in a salon.
        
        Args:
            salon_id: Salon ID for multi-tenant filtering
            active_only: If True, only return active stylists
            limit: Maximum results to return
            
        Returns:
            List of stylists
        """
        return await self.get_by_role(
            role="stylist",
            salon_id=salon_id,
            active_only=active_only,
            limit=limit,
        )
    
    async def get_managers(
        self,
        salon_id: str,
        limit: int = 10,
    ) -> List[Staff]:
        """Get all managers in a salon.
        
        Args:
            salon_id: Salon ID for multi-tenant filtering
            limit: Maximum results to return
            
        Returns:
            List of managers
        """
        return await self.get_by_role(
            role="manager",
            salon_id=salon_id,
            limit=limit,
        )
    
    async def get_receptionists(
        self,
        salon_id: str,
        limit: int = 10,
    ) -> List[Staff]:
        """Get all receptionists in a salon.
        
        Args:
            salon_id: Salon ID for multi-tenant filtering
            limit: Maximum results to return
            
        Returns:
            List of receptionists
        """
        return await self.get_by_role(
            role="receptionist",
            salon_id=salon_id,
            limit=limit,
        )
    
    async def update_availability(
        self,
        staff_id: str,
        is_available: bool,
        salon_id: str,
    ) -> Optional[Staff]:
        """Update staff availability status.
        
        Args:
            staff_id: Staff document ID
            is_available: New availability status
            salon_id: Salon ID for verification
            
        Returns:
            Updated staff if successful
        """
        staff = await self.get(staff_id)
        if not staff or staff.salon_id != salon_id:
            return None
        
        return await self.update(staff_id, {"is_available": is_available})
    
    async def update_status(
        self,
        staff_id: str,
        status: StaffStatus,
        salon_id: str,
    ) -> Optional[Staff]:
        """Update staff employment status.
        
        Args:
            staff_id: Staff document ID
            status: New status (active, inactive, on_leave, terminated)
            salon_id: Salon ID for verification
            
        Returns:
            Updated staff if successful
        """
        staff = await self.get(staff_id)
        if not staff or staff.salon_id != salon_id:
            return None
        
        return await self.update(staff_id, {
            "status": status.value if isinstance(status, StaffStatus) else status,
        })
    
    async def add_skill(
        self,
        staff_id: str,
        skill_data: Dict[str, Any],
        salon_id: str,
    ) -> Optional[Staff]:
        """Add a skill to a staff member.
        
        Args:
            staff_id: Staff document ID
            skill_data: Skill data (name, level, service_ids)
            salon_id: Salon ID for verification
            
        Returns:
            Updated staff if successful
        """
        staff = await self.get(staff_id)
        if not staff or staff.salon_id != salon_id:
            return None
        
        # Get current skills
        current_skills = [s.model_dump() for s in staff.skills] if staff.skills else []
        current_skills.append(skill_data)
        
        return await self.update(staff_id, {"skills": current_skills})
    
    async def update_commission(
        self,
        staff_id: str,
        commission_data: Dict[str, Any],
        salon_id: str,
    ) -> Optional[Staff]:
        """Update staff commission settings.
        
        Args:
            staff_id: Staff document ID
            commission_data: Commission configuration
            salon_id: Salon ID for verification
            
        Returns:
            Updated staff if successful
        """
        staff = await self.get(staff_id)
        if not staff or staff.salon_id != salon_id:
            return None
        
        return await self.update(staff_id, {"commission": commission_data})
    
    async def get_staff_for_service(
        self,
        service_id: str,
        salon_id: str,
        limit: int = 20,
    ) -> List[Staff]:
        """Get staff members who can perform a specific service.
        
        Args:
            service_id: Service document ID
            salon_id: Salon ID for multi-tenant filtering
            limit: Maximum results to return
            
        Returns:
            List of staff members who can perform the service
        """
        try:
            staff_list = await self.list(
                salon_id=salon_id,
                filters=[("status", "==", "active")],
                limit=limit * 2,
            )
            
            # Filter by service in skills
            results = []
            for staff in staff_list:
                if staff.skills:
                    for skill in staff.skills:
                        if skill.service_ids and service_id in skill.service_ids:
                            results.append(staff)
                            break
            
            return results[:limit]
            
        except Exception as e:
            logger.error(
                "Failed to get staff for service",
                service_id=service_id,
                salon_id=salon_id,
                error=str(e),
            )
            raise
    
    async def get_staff_count(
        self,
        salon_id: str,
        role: Optional[str] = None,
    ) -> int:
        """Get staff count for a salon.
        
        Args:
            salon_id: Salon ID
            role: Optional role filter
            
        Returns:
            Number of staff members
        """
        filters = None
        if role:
            filters = [("role", "==", role)]
        
        return await self.count(salon_id=salon_id, filters=filters)
    
    async def get_active_staff_count(
        self,
        salon_id: str,
    ) -> int:
        """Get count of active staff members.
        
        Args:
            salon_id: Salon ID
            
        Returns:
            Number of active staff members
        """
        return await self.count(
            salon_id=salon_id,
            filters=[("status", "==", "active")],
        )
    
    async def get_staff_on_leave(
        self,
        salon_id: str,
        limit: int = 20,
    ) -> List[Staff]:
        """Get staff members currently on leave.
        
        Args:
            salon_id: Salon ID for multi-tenant filtering
            limit: Maximum results to return
            
        Returns:
            List of staff on leave
        """
        return await self.list(
            salon_id=salon_id,
            filters=[("status", "==", "on_leave")],
            limit=limit,
        )
