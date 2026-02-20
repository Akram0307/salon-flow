"""Customer Firestore Model.

Handles all database operations for customer entities.
"""
from datetime import datetime, date
from typing import List, Optional, Dict, Any

from google.cloud.firestore_v1.base_query import FieldFilter
import structlog

from app.models.base import FirestoreBase
from app.schemas import (
    Customer,
    CustomerCreate,
    CustomerUpdate,
)
from app.schemas.base import PaginatedResponse

logger = structlog.get_logger()


class CustomerModel(FirestoreBase[Customer, CustomerCreate, CustomerUpdate]):
    """Model for customer operations.
    
    Provides CRUD operations and specialized queries for customer entities.
    Customers are salon-specific and track loyalty points, memberships,
    and booking history.
    
    Attributes:
        collection_name: Firestore collection name ('customers')
        model: Pydantic model for Customer
        create_schema: Pydantic schema for creating customers
        update_schema: Pydantic schema for updating customers
    
    Example:
        customer_model = CustomerModel()
        customer = await customer_model.get_by_phone("+919876543210", salon_id="salon_123")
    """
    
    collection_name = "customers"
    id_field = "customer_id"  # Override to use customer_id instead of id
    model = Customer
    create_schema = CustomerCreate
    update_schema = CustomerUpdate
    
    async def get_by_phone(
        self,
        phone: str,
        salon_id: str,
    ) -> Optional[Customer]:
        """Get a customer by phone number within a salon.
        
        Args:
            phone: Customer phone number
            salon_id: Salon ID for multi-tenant filtering
            
        Returns:
            Customer if found, None otherwise
        
        Example:
            customer = await customer_model.get_by_phone("+919876543210", salon_id="salon_123")
        """
        return await self.get_by_field("phone", phone, salon_id=salon_id)
    
    async def get_by_email(
        self,
        email: str,
        salon_id: str,
    ) -> Optional[Customer]:
        """Get a customer by email within a salon.
        
        Args:
            email: Customer email address
            salon_id: Salon ID for multi-tenant filtering
            
        Returns:
            Customer if found, None otherwise
        """
        return await self.get_by_field("email", email, salon_id=salon_id)
    
    async def search_by_name(
        self,
        name: str,
        salon_id: str,
        limit: int = 10,
    ) -> List[Customer]:
        """Search customers by name (prefix match).
        
        Args:
            name: Name prefix to search
            salon_id: Salon ID for multi-tenant filtering
            limit: Maximum results to return
            
        Returns:
            List of matching customers
        """
        return await self.search("name", name, salon_id=salon_id, limit=limit)
    
    async def search_customers(
        self,
        salon_id: str,
        query: str,
        limit: int = 10,
    ) -> List[Customer]:
        """Search customers by name or phone.
        
        Args:
            salon_id: Salon ID for multi-tenant filtering
            query: Search query (name or phone)
            limit: Maximum results to return
            
        Returns:
            List of matching customers
        """
        try:
            # Try to search by name first
            name_results = await self.search_by_name(query, salon_id, limit)
            
            # Also search by phone if query looks like a phone number
            phone_results = []
            if query.replace("+", "").replace(" ", "").isdigit():
                phone_results = await self.list(
                    salon_id=salon_id,
                    filters=[("phone", ">=", query), ("phone", "<", query + "\uf8ff")],
                    limit=limit,
                )
            
            # Combine and deduplicate
            seen_ids = set()
            results = []
            for customer in name_results + phone_results:
                if customer.id not in seen_ids:
                    seen_ids.add(customer.id)
                    results.append(customer)
            
            return results[:limit]
            
        except Exception as e:
            logger.error(
                "Failed to search customers",
                salon_id=salon_id,
                query=query,
                error=str(e),
            )
            raise
    
    async def update_loyalty(
        self,
        customer_id: str,
        points_change: int,
        salon_id: str,
        operation: str = "add",
    ) -> Optional[Customer]:
        """Update customer loyalty points.
        
        Args:
            customer_id: Customer document ID
            points_change: Number of points to add/subtract
            salon_id: Salon ID for verification
            operation: "add" or "subtract" points
            
        Returns:
            Updated customer if successful, None if not found
        """
        try:
            customer = await self.get(customer_id)
            if not customer or customer.salon_id != salon_id:
                return None
            
            current_points = customer.loyalty.points_balance if customer.loyalty else 0
            
            if operation == "add":
                new_balance = current_points + points_change
            else:
                new_balance = max(0, current_points - points_change)
            
            update_data = {
                "loyalty.points_balance": new_balance,
                "loyalty.last_updated": datetime.utcnow().isoformat(),
            }
            
            return await self.update(customer_id, update_data)
            
        except Exception as e:
            logger.error(
                "Failed to update loyalty points",
                customer_id=customer_id,
                error=str(e),
            )
            raise
    
    async def get_membership_customers(
        self,
        salon_id: str,
        active_only: bool = True,
        limit: int = 100,
    ) -> List[Customer]:
        """Get customers with memberships.
        
        Args:
            salon_id: Salon ID for multi-tenant filtering
            active_only: If True, only return active memberships
            limit: Maximum results to return
            
        Returns:
            List of customers with memberships
        """
        filters = [("membership.is_member", "==", True)]
        
        if active_only:
            filters.append(("membership.status", "==", "active"))
        
        return await self.list(
            salon_id=salon_id,
            filters=filters,
            order_by="membership.valid_till",
            limit=limit,
        )
    
    async def get_loyalty_customers(
        self,
        salon_id: str,
        min_points: int = 100,
        limit: int = 100,
    ) -> List[Customer]:
        """Get customers with loyalty points above threshold.
        
        Args:
            salon_id: Salon ID for multi-tenant filtering
            min_points: Minimum loyalty points balance
            limit: Maximum results to return
            
        Returns:
            List of customers with high loyalty points
        """
        return await self.list(
            salon_id=salon_id,
            filters=[("loyalty.points_balance", ">=", min_points)],
            order_by="loyalty.points_balance",
            order_direction="DESCENDING",
            limit=limit,
        )
    
    async def get_by_birthday_month(
        self,
        salon_id: str,
        month: int,
        limit: int = 100,
    ) -> List[Customer]:
        """Get customers with birthdays in a specific month.
        
        Args:
            salon_id: Salon ID for multi-tenant filtering
            month: Month number (1-12)
            limit: Maximum results to return
            
        Returns:
            List of customers with birthdays in the month
        """
        # Note: Firestore doesn't support month extraction directly
        # This requires a composite query or client-side filtering
        # For now, we'll fetch all and filter client-side
        # In production, consider storing birthday_month as a separate field
        
        customers = await self.list(
            salon_id=salon_id,
            filters=[("date_of_birth", "!=", None)],
            limit=limit * 3,  # Fetch more to account for filtering
        )
        
        # Filter by month
        return [
            c for c in customers
            if c.date_of_birth and c.date_of_birth.month == month
        ][:limit]
    
    async def get_top_customers(
        self,
        salon_id: str,
        by: str = "total_spent",
        limit: int = 10,
    ) -> List[Customer]:
        """Get top customers by spending or visits.
        
        Args:
            salon_id: Salon ID for multi-tenant filtering
            by: Sort by "total_spent" or "total_visits"
            limit: Maximum results to return
            
        Returns:
            List of top customers
        """
        order_field = f"stats.{by}"
        
        return await self.list(
            salon_id=salon_id,
            order_by=order_field,
            order_direction="DESCENDING",
            limit=limit,
        )
    
    async def get_inactive_customers(
        self,
        salon_id: str,
        days_inactive: int = 90,
        limit: int = 100,
    ) -> List[Customer]:
        """Get customers who haven't visited in a while.
        
        Args:
            salon_id: Salon ID for multi-tenant filtering
            days_inactive: Number of days since last visit
            limit: Maximum results to return
            
        Returns:
            List of inactive customers
        """
        from datetime import timedelta
        
        threshold = date.today() - timedelta(days=days_inactive)
        
        return await self.list(
            salon_id=salon_id,
            filters=[("stats.last_visit", "<", threshold.isoformat())],
            order_by="stats.last_visit",
            order_direction="DESCENDING",
            limit=limit,
        )
    
    async def get_new_customers(
        self,
        salon_id: str,
        days: int = 30,
        limit: int = 100,
    ) -> List[Customer]:
        """Get recently registered customers.
        
        Args:
            salon_id: Salon ID for multi-tenant filtering
            days: Number of days to look back
            limit: Maximum results to return
            
        Returns:
            List of new customers
        """
        from datetime import timedelta
        
        threshold = datetime.utcnow() - timedelta(days=days)
        
        return await self.list(
            salon_id=salon_id,
            filters=[("created_at", ">=", threshold.isoformat())],
            order_by="created_at",
            order_direction="DESCENDING",
            limit=limit,
        )
    
    async def update_membership(
        self,
        customer_id: str,
        membership_data: Dict[str, Any],
    ) -> Optional[Customer]:
        """Update customer membership details.
        
        Args:
            customer_id: Customer document ID
            membership_data: Membership update data
            
        Returns:
            Updated customer if successful
        """
        return await self.update(customer_id, {"membership": membership_data})
    
    async def increment_stats(
        self,
        customer_id: str,
        field: str,
        value: float = 1,
    ) -> bool:
        """Atomically increment a customer stat.
        
        Args:
            customer_id: Customer document ID
            field: Stat field to increment (e.g., "total_visits", "total_spent")
            value: Amount to increment
            
        Returns:
            True if successful
        """
        try:
            doc_ref = self.collection.document(customer_id)
            await doc_ref.update({
                f"stats.{field}": value,
                "stats.last_visit": date.today().isoformat(),
                "updated_at": datetime.utcnow(),
            })
            return True
        except Exception as e:
            logger.error(
                "Failed to increment customer stats",
                customer_id=customer_id,
                field=field,
                error=str(e),
            )
            return False
    
    async def get_customer_count(
        self,
        salon_id: str,
    ) -> int:
        """Get total customer count for a salon.
        
        Args:
            salon_id: Salon ID
            
        Returns:
            Total number of customers
        """
        return await self.count(salon_id=salon_id)
    
    async def get_customers_by_gender(
        self,
        salon_id: str,
        gender: str,
        limit: int = 100,
    ) -> List[Customer]:
        """Get customers filtered by gender.
        
        Args:
            salon_id: Salon ID for multi-tenant filtering
            gender: Gender filter value
            limit: Maximum results to return
            
        Returns:
            List of customers matching gender
        """
        return await self.list(
            salon_id=salon_id,
            filters=[("gender", "==", gender)],
            limit=limit,
        )
