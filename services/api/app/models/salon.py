"""Salon Firestore Model.

Handles all database operations for salon/tenant entities.
"""
from datetime import datetime, date
from typing import List, Optional, Dict, Any

from google.cloud.firestore_v1.base_query import FieldFilter
import structlog

from app.models.base import FirestoreBase
from app.schemas import (
    Salon,
    SalonCreate,
    SalonUpdate,
    SubscriptionStatus,
    SubscriptionPlan,
)
from app.schemas.base import PaginatedResponse

logger = structlog.get_logger()


class SalonModel(FirestoreBase[Salon, SalonCreate, SalonUpdate]):
    """Model for salon/tenant operations.
    
    Provides CRUD operations and specialized queries for salon entities.
    Each salon represents a tenant in the multi-tenant architecture.
    
    Attributes:
        collection_name: Firestore collection name ('salons')
        model: Pydantic model for Salon
        create_schema: Pydantic schema for creating salons
        update_schema: Pydantic schema for updating salons
    
    Example:
        salon_model = SalonModel()
        salon = await salon_model.get_by_slug("jawed-habib-kurnool")
    """
    
    collection_name = "salons"
    model = Salon
    create_schema = SalonCreate
    update_schema = SalonUpdate
    
    async def get_by_slug(self, slug: str) -> Optional[Salon]:
        """Get a salon by its URL slug.
        
        Args:
            slug: Unique URL-friendly identifier for the salon
            
        Returns:
            Salon if found, None otherwise
        
        Example:
            salon = await salon_model.get_by_slug("jawed-habib-kurnool")
        """
        return await self.get_by_field("slug", slug)
    
    async def get_by_phone(self, phone: str) -> Optional[Salon]:
        """Get a salon by phone number.
        
        Args:
            phone: Primary contact phone number
            
        Returns:
            Salon if found, None otherwise
        """
        return await self.get_by_field("contact.primary_phone", phone)
    
    async def get_by_email(self, email: str) -> Optional[Salon]:
        """Get a salon by email address.
        
        Args:
            email: Primary contact email
            
        Returns:
            Salon if found, None otherwise
        """
        return await self.get_by_field("contact.email", email)
    
    async def get_by_owner(self, owner_id: str) -> List[Salon]:
        """Get all salons owned by a specific user.
        
        Args:
            owner_id: Firebase Auth UID of the owner
            
        Returns:
            List of salons owned by the user
        """
        return await self.list(
            filters=[("owner_id", "==", owner_id)],
            order_by="created_at",
            order_direction="DESCENDING",
        )
    
    async def get_active_salons(
        self,
        limit: int = 100,
    ) -> List[Salon]:
        """Get all active salons.
        
        Args:
            limit: Maximum number of salons to return
            
        Returns:
            List of active salons
        """
        return await self.list(
            filters=[("status", "==", "active")],
            order_by="created_at",
            order_direction="DESCENDING",
            limit=limit,
        )
    
    async def update_subscription(
        self,
        salon_id: str,
        plan: SubscriptionPlan,
        status: SubscriptionStatus,
        expires_at: Optional[date] = None,
        stripe_subscription_id: Optional[str] = None,
    ) -> Optional[Salon]:
        """Update salon subscription details.
        
        Args:
            salon_id: Salon document ID
            plan: New subscription plan
            status: New subscription status
            expires_at: Subscription expiration date
            stripe_subscription_id: Stripe subscription ID for billing
            
        Returns:
            Updated salon if successful, None if not found
        """
        update_data = {
            "subscription": {
                "plan": plan.value if isinstance(plan, SubscriptionPlan) else plan,
                "status": status.value if isinstance(status, SubscriptionStatus) else status,
                "updated_at": datetime.utcnow().isoformat(),
            }
        }
        
        if expires_at:
            update_data["subscription"]["expires_at"] = expires_at.isoformat()
        
        if stripe_subscription_id:
            update_data["subscription"]["stripe_subscription_id"] = stripe_subscription_id
        
        return await self.update(salon_id, update_data)
    
    async def get_expiring_subscriptions(
        self,
        days_before: int = 15,
        limit: int = 100,
    ) -> List[Salon]:
        """Get salons with subscriptions expiring soon.
        
        Args:
            days_before: Number of days before expiration to check
            limit: Maximum number of salons to return
            
        Returns:
            List of salons with expiring subscriptions
        """
        from datetime import timedelta
        
        today = date.today()
        expiry_threshold = today + timedelta(days=days_before)
        
        # Query for active subscriptions expiring within threshold
        return await self.list(
            filters=[
                ("subscription.status", "==", "active"),
                ("subscription.expires_at", "<=", expiry_threshold.isoformat()),
            ],
            order_by="subscription.expires_at",
            limit=limit,
        )
    
    async def get_trial_ending(
        self,
        days_before: int = 3,
        limit: int = 100,
    ) -> List[Salon]:
        """Get salons with trials ending soon.
        
        Args:
            days_before: Number of days before trial ends
            limit: Maximum number of salons to return
            
        Returns:
            List of salons with trials ending
        """
        from datetime import timedelta
        
        today = date.today()
        trial_end = today + timedelta(days=days_before)
        
        return await self.list(
            filters=[
                ("subscription.status", "==", "trial"),
                ("subscription.expires_at", "<=", trial_end.isoformat()),
            ],
            order_by="subscription.expires_at",
            limit=limit,
        )
    
    async def update_settings(
        self,
        salon_id: str,
        settings: Dict[str, Any],
    ) -> Optional[Salon]:
        """Update salon settings.
        
        Args:
            salon_id: Salon document ID
            settings: Dictionary of settings to update
            
        Returns:
            Updated salon if successful, None if not found
        """
        return await self.update(salon_id, {"settings": settings})
    
    async def update_layout(
        self,
        salon_id: str,
        layout: Dict[str, Any],
    ) -> Optional[Salon]:
        """Update salon layout configuration.
        
        Args:
            salon_id: Salon document ID
            layout: Layout configuration dictionary
            
        Returns:
            Updated salon if successful, None if not found
        """
        return await self.update(salon_id, {"layout": layout})
    
    async def search_by_name(
        self,
        name: str,
        limit: int = 10,
    ) -> List[Salon]:
        """Search salons by name (prefix match).
        
        Args:
            name: Name prefix to search
            limit: Maximum results to return
            
        Returns:
            List of matching salons
        """
        return await self.search("name", name, limit=limit)
    
    async def get_by_city(
        self,
        city: str,
        limit: int = 50,
    ) -> List[Salon]:
        """Get salons by city.
        
        Args:
            city: City name
            limit: Maximum results to return
            
        Returns:
            List of salons in the city
        """
        return await self.list(
            filters=[("address.city", "==", city)],
            order_by="name",
            limit=limit,
        )
    
    async def get_by_pincode(
        self,
        pincode: str,
        limit: int = 50,
    ) -> List[Salon]:
        """Get salons by pincode.
        
        Args:
            pincode: Postal code
            limit: Maximum results to return
            
        Returns:
            List of salons in the pincode area
        """
        return await self.list(
            filters=[("address.pincode", "==", pincode)],
            order_by="name",
            limit=limit,
        )
    
    async def increment_customer_count(
        self,
        salon_id: str,
        increment: int = 1,
    ) -> bool:
        """Atomically increment customer count.
        
        Args:
            salon_id: Salon document ID
            increment: Amount to increment (default 1)
            
        Returns:
            True if successful
        """
        try:
            doc_ref = self.collection.document(salon_id)
            await doc_ref.update({
                "stats.total_customers": increment,
                "updated_at": datetime.utcnow(),
            })
            return True
        except Exception as e:
            logger.error(
                "Failed to increment customer count",
                salon_id=salon_id,
                error=str(e),
            )
            return False
    
    async def get_salon_stats(
        self,
        salon_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Get salon statistics.
        
        Args:
            salon_id: Salon document ID
            
        Returns:
            Statistics dictionary if salon exists
        """
        salon = await self.get(salon_id)
        if salon:
            return salon.stats.model_dump() if salon.stats else {}
        return None
