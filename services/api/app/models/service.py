"""Service Firestore Model.

Handles all database operations for service entities.
"""
from datetime import datetime, date
from typing import List, Optional, Dict, Any

from google.cloud.firestore_v1.base_query import FieldFilter
import structlog

from app.models.base import FirestoreBase
from app.schemas import (
    Service,
    ServiceCreate,
    ServiceUpdate,
    ServiceCategory,
)
from app.schemas.base import PaginatedResponse

logger = structlog.get_logger()


class ServiceModel(FirestoreBase[Service, ServiceCreate, ServiceUpdate]):
    """Model for service operations.
    
    Provides CRUD operations and specialized queries for service entities.
    Services are salon-specific offerings with pricing, duration, and resource requirements.
    
    Attributes:
        collection_name: Firestore collection name ('services')
        model: Pydantic model for Service
        create_schema: Pydantic schema for creating services
        update_schema: Pydantic schema for updating services
    
    Example:
        service_model = ServiceModel()
        services = await service_model.get_by_category("haircut", salon_id="salon_123")
    """
    
    collection_name = "services"
    model = Service
    create_schema = ServiceCreate
    update_schema = ServiceUpdate
    
    async def get_by_category(
        self,
        category: str,
        salon_id: str,
        active_only: bool = True,
        limit: int = 50,
    ) -> List[Service]:
        """Get services by category.
        
        Args:
            category: Service category (haircut, hair_color, facial, etc.)
            salon_id: Salon ID for multi-tenant filtering
            active_only: If True, only return active services
            limit: Maximum results to return
            
        Returns:
            List of services in the category
        
        Example:
            services = await service_model.get_by_category("haircut", salon_id="salon_123")
        """
        filters = [("category", "==", category)]
        
        if active_only:
            filters.append(("is_active", "==", True))
        
        return await self.list(
            salon_id=salon_id,
            filters=filters,
            order_by="name",
            limit=limit,
        )
    
    async def get_active_services(
        self,
        salon_id: str,
        limit: int = 100,
    ) -> List[Service]:
        """Get all active services for a salon.
        
        Args:
            salon_id: Salon ID for multi-tenant filtering
            limit: Maximum results to return
            
        Returns:
            List of active services
        """
        return await self.list(
            salon_id=salon_id,
            filters=[("is_active", "==", True)],
            order_by="name",
            limit=limit,
        )
    
    async def get_services_for_resource(
        self,
        resource_type: str,
        salon_id: str,
        active_only: bool = True,
        limit: int = 50,
    ) -> List[Service]:
        """Get services that require a specific resource type.
        
        Args:
            resource_type: Resource type (chair_mens, chair_womens, room_bridal, etc.)
            salon_id: Salon ID for multi-tenant filtering
            active_only: If True, only return active services
            limit: Maximum results to return
            
        Returns:
            List of services requiring the resource type
        """
        try:
            filters = [("resource_requirement.resource_type", "==", resource_type)]
            
            if active_only:
                filters.append(("is_active", "==", True))
            
            return await self.list(
                salon_id=salon_id,
                filters=filters,
                order_by="name",
                limit=limit,
            )
        except Exception as e:
            logger.error(
                "Failed to get services for resource",
                resource_type=resource_type,
                salon_id=salon_id,
                error=str(e),
            )
            raise
    
    async def get_by_name(
        self,
        name: str,
        salon_id: str,
    ) -> Optional[Service]:
        """Get a service by name within a salon.
        
        Args:
            name: Service name
            salon_id: Salon ID for multi-tenant filtering
            
        Returns:
            Service if found, None otherwise
        """
        return await self.get_by_field("name", name, salon_id=salon_id)
    
    async def search_services(
        self,
        query: str,
        salon_id: str,
        limit: int = 10,
    ) -> List[Service]:
        """Search services by name (prefix match).
        
        Args:
            query: Search query
            salon_id: Salon ID for multi-tenant filtering
            limit: Maximum results to return
            
        Returns:
            List of matching services
        """
        return await self.search("name", query, salon_id=salon_id, limit=limit)
    
    async def get_by_price_range(
        self,
        min_price: float,
        max_price: float,
        salon_id: str,
        active_only: bool = True,
        limit: int = 50,
    ) -> List[Service]:
        """Get services within a price range.
        
        Args:
            min_price: Minimum price
            max_price: Maximum price
            salon_id: Salon ID for multi-tenant filtering
            active_only: If True, only return active services
            limit: Maximum results to return
            
        Returns:
            List of services in the price range
        """
        filters = [
            ("pricing.base_price", ">=", min_price),
            ("pricing.base_price", "<=", max_price),
        ]
        
        if active_only:
            filters.append(("is_active", "==", True))
        
        return await self.list(
            salon_id=salon_id,
            filters=filters,
            order_by="pricing.base_price",
            limit=limit,
        )
    
    async def get_by_duration_range(
        self,
        min_minutes: int,
        max_minutes: int,
        salon_id: str,
        active_only: bool = True,
        limit: int = 50,
    ) -> List[Service]:
        """Get services within a duration range.
        
        Args:
            min_minutes: Minimum duration in minutes
            max_minutes: Maximum duration in minutes
            salon_id: Salon ID for multi-tenant filtering
            active_only: If True, only return active services
            limit: Maximum results to return
            
        Returns:
            List of services in the duration range
        """
        filters = [
            ("duration.standard_minutes", ">=", min_minutes),
            ("duration.standard_minutes", "<=", max_minutes),
        ]
        
        if active_only:
            filters.append(("is_active", "==", True))
        
        return await self.list(
            salon_id=salon_id,
            filters=filters,
            order_by="duration.standard_minutes",
            limit=limit,
        )
    
    async def get_popular_services(
        self,
        salon_id: str,
        limit: int = 10,
    ) -> List[Service]:
        """Get most popular services based on booking count.
        
        Args:
            salon_id: Salon ID for multi-tenant filtering
            limit: Maximum results to return
            
        Returns:
            List of popular services
        """
        return await self.list(
            salon_id=salon_id,
            filters=[("is_active", "==", True)],
            order_by="stats.booking_count",
            order_direction="DESCENDING",
            limit=limit,
        )
    
    async def get_services_by_gender(
        self,
        gender: str,
        salon_id: str,
        active_only: bool = True,
        limit: int = 50,
    ) -> List[Service]:
        """Get services for a specific gender.
        
        Args:
            gender: Gender filter (male, female, unisex)
            salon_id: Salon ID for multi-tenant filtering
            active_only: If True, only return active services
            limit: Maximum results to return
            
        Returns:
            List of services for the gender
        """
        filters = [("gender", "==", gender)]
        
        if active_only:
            filters.append(("is_active", "==", True))
        
        return await self.list(
            salon_id=salon_id,
            filters=filters,
            order_by="name",
            limit=limit,
        )
    
    async def get_grouped_by_category(
        self,
        salon_id: str,
        active_only: bool = True,
    ) -> Dict[str, List[Service]]:
        """Get services grouped by category.
        
        Args:
            salon_id: Salon ID for multi-tenant filtering
            active_only: If True, only return active services
            
        Returns:
            Dictionary mapping category names to lists of services
        """
        services = await self.list(
            salon_id=salon_id,
            filters=[("is_active", "==", True)] if active_only else None,
            order_by="category",
            limit=200,
        )
        
        grouped = {}
        for service in services:
            category = service.category.value if hasattr(service.category, 'value') else service.category
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(service)
        
        return grouped
    
    async def update_pricing(
        self,
        service_id: str,
        pricing_data: Dict[str, Any],
        salon_id: str,
    ) -> Optional[Service]:
        """Update service pricing.
        
        Args:
            service_id: Service document ID
            pricing_data: New pricing configuration
            salon_id: Salon ID for verification
            
        Returns:
            Updated service if successful
        """
        service = await self.get(service_id)
        if not service or service.salon_id != salon_id:
            return None
        
        return await self.update(service_id, {"pricing": pricing_data})
    
    async def update_duration(
        self,
        service_id: str,
        duration_data: Dict[str, Any],
        salon_id: str,
    ) -> Optional[Service]:
        """Update service duration settings.
        
        Args:
            service_id: Service document ID
            duration_data: New duration configuration
            salon_id: Salon ID for verification
            
        Returns:
            Updated service if successful
        """
        service = await self.get(service_id)
        if not service or service.salon_id != salon_id:
            return None
        
        return await self.update(service_id, {"duration": duration_data})
    
    async def activate_service(
        self,
        service_id: str,
        salon_id: str,
    ) -> Optional[Service]:
        """Activate a service.
        
        Args:
            service_id: Service document ID
            salon_id: Salon ID for verification
            
        Returns:
            Updated service if successful
        """
        service = await self.get(service_id)
        if not service or service.salon_id != salon_id:
            return None
        
        return await self.update(service_id, {"is_active": True})
    
    async def deactivate_service(
        self,
        service_id: str,
        salon_id: str,
    ) -> Optional[Service]:
        """Deactivate a service.
        
        Args:
            service_id: Service document ID
            salon_id: Salon ID for verification
            
        Returns:
            Updated service if successful
        """
        service = await self.get(service_id)
        if not service or service.salon_id != salon_id:
            return None
        
        return await self.update(service_id, {"is_active": False})
    
    async def increment_booking_count(
        self,
        service_id: str,
    ) -> bool:
        """Atomically increment booking count for a service.
        
        Args:
            service_id: Service document ID
            
        Returns:
            True if successful
        """
        try:
            doc_ref = self.collection.document(service_id)
            await doc_ref.update({
                "stats.booking_count": 1,
                "stats.last_booked": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow(),
            })
            return True
        except Exception as e:
            logger.error(
                "Failed to increment booking count",
                service_id=service_id,
                error=str(e),
            )
            return False
    
    async def get_service_count(
        self,
        salon_id: str,
        category: Optional[str] = None,
        active_only: bool = False,
    ) -> int:
        """Get service count for a salon.
        
        Args:
            salon_id: Salon ID
            category: Optional category filter
            active_only: If True, only count active services
            
        Returns:
            Number of services
        """
        filters = []
        if category:
            filters.append(("category", "==", category))
        if active_only:
            filters.append(("is_active", "==", True))
        
        return await self.count(
            salon_id=salon_id,
            filters=filters if filters else None,
        )
    
    async def get_services_for_staff(
        self,
        staff_id: str,
        salon_id: str,
        limit: int = 50,
    ) -> List[Service]:
        """Get services that a staff member can perform.
        
        Args:
            staff_id: Staff document ID
            salon_id: Salon ID for multi-tenant filtering
            limit: Maximum results to return
            
        Returns:
            List of services the staff can perform
        """
        try:
            # This requires checking staff skills
            # For now, return all active services
            # In production, filter based on staff skills
            return await self.get_active_services(salon_id=salon_id, limit=limit)
        except Exception as e:
            logger.error(
                "Failed to get services for staff",
                staff_id=staff_id,
                salon_id=salon_id,
                error=str(e),
            )
            raise
