"""Resource Firestore Model.

Handles all database operations for resource entities.
"""
from datetime import datetime, date, time
from typing import List, Optional, Dict, Any

from google.cloud.firestore_v1.base_query import FieldFilter
import structlog

from app.models.base import FirestoreBase
from app.schemas import (
    Resource,
    ResourceCreate,
    ResourceUpdate,
    ResourceType,
    ResourceStatus,
)
from app.schemas.base import PaginatedResponse

logger = structlog.get_logger()


class ResourceModel(FirestoreBase[Resource, ResourceCreate, ResourceUpdate]):
    """Model for resource operations.
    
    Provides CRUD operations and specialized queries for resource entities.
    Resources are physical assets like chairs, rooms, and equipment.
    
    Attributes:
        collection_name: Firestore collection name ('resources')
        model: Pydantic model for Resource
        create_schema: Pydantic schema for creating resources
        update_schema: Pydantic schema for updating resources
    
    Example:
        resource_model = ResourceModel()
        chairs = await resource_model.get_by_type("chair_mens", salon_id="salon_123")
    """
    
    collection_name = "resources"
    model = Resource
    create_schema = ResourceCreate
    update_schema = ResourceUpdate
    
    async def get_by_type(
        self,
        resource_type: str,
        salon_id: str,
        status: Optional[str] = None,
        limit: int = 50,
    ) -> List[Resource]:
        """Get resources by type.
        
        Args:
            resource_type: Resource type (chair_mens, chair_womens, room_bridal, etc.)
            salon_id: Salon ID for multi-tenant filtering
            status: Optional status filter
            limit: Maximum results to return
            
        Returns:
            List of resources of the specified type
        
        Example:
            chairs = await resource_model.get_by_type("chair_mens", salon_id="salon_123")
        """
        filters = [("type", "==", resource_type)]
        
        if status:
            filters.append(("status", "==", status))
        
        return await self.list(
            salon_id=salon_id,
            filters=filters,
            order_by="name",
            limit=limit,
        )
    
    async def get_available_resources(
        self,
        salon_id: str,
        resource_type: Optional[str] = None,
        limit: int = 50,
    ) -> List[Resource]:
        """Get all available resources.
        
        Args:
            salon_id: Salon ID for multi-tenant filtering
            resource_type: Optional resource type filter
            limit: Maximum results to return
            
        Returns:
            List of available resources
        """
        filters = [("status", "==", "available")]
        
        if resource_type:
            filters.append(("type", "==", resource_type))
        
        return await self.list(
            salon_id=salon_id,
            filters=filters,
            order_by="name",
            limit=limit,
        )
    
    async def get_by_name(
        self,
        name: str,
        salon_id: str,
    ) -> Optional[Resource]:
        """Get a resource by name.
        
        Args:
            name: Resource name
            salon_id: Salon ID for multi-tenant filtering
            
        Returns:
            Resource if found, None otherwise
        """
        return await self.get_by_field("name", name, salon_id=salon_id)
    
    async def get_chairs(
        self,
        salon_id: str,
        gender: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Resource]:
        """Get all chair resources.
        
        Args:
            salon_id: Salon ID for multi-tenant filtering
            gender: Optional gender filter (mens, womens)
            status: Optional status filter
            
        Returns:
            List of chair resources
        """
        if gender:
            resource_type = f"chair_{gender}"
            return await self.get_by_type(resource_type, salon_id, status)
        
        # Get both mens and womens chairs
        mens_chairs = await self.get_by_type("chair_mens", salon_id, status)
        womens_chairs = await self.get_by_type("chair_womens", salon_id, status)
        
        return mens_chairs + womens_chairs
    
    async def get_rooms(
        self,
        salon_id: str,
        room_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Resource]:
        """Get all room resources.
        
        Args:
            salon_id: Salon ID for multi-tenant filtering
            room_type: Optional room type (bridal, treatment, spa)
            status: Optional status filter
            
        Returns:
            List of room resources
        """
        if room_type:
            resource_type = f"room_{room_type}"
            return await self.get_by_type(resource_type, salon_id, status)
        
        # Get all room types
        rooms = []
        for rtype in ["room_bridal", "room_treatment", "room_spa"]:
            rooms.extend(await self.get_by_type(rtype, salon_id, status))
        
        return rooms
    
    async def update_status(
        self,
        resource_id: str,
        status: ResourceStatus,
        salon_id: str,
        notes: Optional[str] = None,
    ) -> Optional[Resource]:
        """Update resource status.
        
        Args:
            resource_id: Resource document ID
            status: New status
            salon_id: Salon ID for verification
            notes: Optional status change notes
            
        Returns:
            Updated resource if successful
        """
        resource = await self.get(resource_id)
        if not resource or resource.salon_id != salon_id:
            return None
        
        update_data = {
            "status": status.value if isinstance(status, ResourceStatus) else status,
            "status_updated_at": datetime.utcnow().isoformat(),
        }
        
        if notes:
            update_data["status_notes"] = notes
        
        return await self.update(resource_id, update_data)
    
    async def set_maintenance(
        self,
        resource_id: str,
        salon_id: str,
        reason: str,
        expected_return: Optional[date] = None,
    ) -> Optional[Resource]:
        """Set resource to maintenance status.
        
        Args:
            resource_id: Resource document ID
            salon_id: Salon ID for verification
            reason: Maintenance reason
            expected_return: Expected return date
            
        Returns:
            Updated resource if successful
        """
        resource = await self.get(resource_id)
        if not resource or resource.salon_id != salon_id:
            return None
        
        update_data = {
            "status": "maintenance",
            "maintenance": {
                "reason": reason,
                "started_at": datetime.utcnow().isoformat(),
                "expected_return": expected_return.isoformat() if expected_return else None,
            },
        }
        
        return await self.update(resource_id, update_data)
    
    async def complete_maintenance(
        self,
        resource_id: str,
        salon_id: str,
        notes: Optional[str] = None,
    ) -> Optional[Resource]:
        """Complete maintenance and set resource back to available.
        
        Args:
            resource_id: Resource document ID
            salon_id: Salon ID for verification
            notes: Optional completion notes
            
        Returns:
            Updated resource if successful
        """
        resource = await self.get(resource_id)
        if not resource or resource.salon_id != salon_id:
            return None
        
        update_data = {
            "status": "available",
            "maintenance": {
                "completed_at": datetime.utcnow().isoformat(),
                "completion_notes": notes,
            },
        }
        
        return await self.update(resource_id, update_data)
    
    async def assign_to_staff(
        self,
        resource_id: str,
        staff_id: str,
        salon_id: str,
    ) -> Optional[Resource]:
        """Assign a resource to a staff member.
        
        Args:
            resource_id: Resource document ID
            staff_id: Staff document ID
            salon_id: Salon ID for verification
            
        Returns:
            Updated resource if successful
        """
        resource = await self.get(resource_id)
        if not resource or resource.salon_id != salon_id:
            return None
        
        return await self.update(resource_id, {
            "assigned_staff_id": staff_id,
            "assigned_at": datetime.utcnow().isoformat(),
        })
    
    async def unassign(
        self,
        resource_id: str,
        salon_id: str,
    ) -> Optional[Resource]:
        """Unassign a resource from staff.
        
        Args:
            resource_id: Resource document ID
            salon_id: Salon ID for verification
            
        Returns:
            Updated resource if successful
        """
        resource = await self.get(resource_id)
        if not resource or resource.salon_id != salon_id:
            return None
        
        return await self.update(resource_id, {
            "assigned_staff_id": None,
            "unassigned_at": datetime.utcnow().isoformat(),
        })
    
    async def get_resource_count(
        self,
        salon_id: str,
        resource_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> int:
        """Get resource count for a salon.
        
        Args:
            salon_id: Salon ID
            resource_type: Optional resource type filter
            status: Optional status filter
            
        Returns:
            Number of resources
        """
        filters = []
        if resource_type:
            filters.append(("type", "==", resource_type))
        if status:
            filters.append(("status", "==", status))
        
        return await self.count(
            salon_id=salon_id,
            filters=filters if filters else None,
        )
    
    async def get_resource_summary(
        self,
        salon_id: str,
    ) -> Dict[str, Any]:
        """Get resource summary for a salon.
        
        Args:
            salon_id: Salon ID
            
        Returns:
            Resource summary by type and status
        """
        resources = await self.list(
            salon_id=salon_id,
            limit=200,
        )
        
        summary = {
            "total": len(resources),
            "by_type": {},
            "by_status": {},
        }
        
        for resource in resources:
            rtype = resource.type.value if hasattr(resource.type, 'value') else resource.type
            status = resource.status.value if hasattr(resource.status, 'value') else resource.status
            
            # Count by type
            if rtype not in summary["by_type"]:
                summary["by_type"][rtype] = 0
            summary["by_type"][rtype] += 1
            
            # Count by status
            if status not in summary["by_status"]:
                summary["by_status"][status] = 0
            summary["by_status"][status] += 1
        
        return summary
    
    async def bulk_create_resources(
        self,
        salon_id: str,
        resources_data: List[Dict[str, Any]],
    ) -> List[Resource]:
        """Bulk create resources for a salon.
        
        Args:
            salon_id: Salon ID
            resources_data: List of resource data dictionaries
            
        Returns:
            List of created resources
        """
        created_resources = []
        
        for data in resources_data:
            data["salon_id"] = salon_id
            resource = await self.create(data)
            created_resources.append(resource)
        
        return created_resources
