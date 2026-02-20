"""Membership Firestore Model.

Handles all database operations for membership entities.
"""
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any

from google.cloud.firestore_v1.base_query import FieldFilter
import structlog

from app.models.base import FirestoreBase
from app.schemas import (
    Membership,
    MembershipCreate,
    MembershipUpdate,
    MembershipStatus,
    MembershipPlanType,
)
from app.schemas.base import PaginatedResponse

logger = structlog.get_logger()


class MembershipModel(FirestoreBase[Membership, MembershipCreate, MembershipUpdate]):
    """Model for membership operations.
    
    Provides CRUD operations and specialized queries for membership entities.
    Memberships are prepaid plans that customers can purchase for discounts.
    
    Attributes:
        collection_name: Firestore collection name ('memberships')
        model: Pydantic model for Membership
        create_schema: Pydantic schema for creating memberships
        update_schema: Pydantic schema for updating memberships
    
    Example:
        membership_model = MembershipModel()
        active = await membership_model.get_active(salon_id="salon_123")
    """
    
    collection_name = "memberships"
    model = Membership
    create_schema = MembershipCreate
    update_schema = MembershipUpdate
    
    async def get_active(
        self,
        salon_id: str,
        limit: int = 100,
    ) -> List[Membership]:
        """Get all active memberships.
        
        Args:
            salon_id: Salon ID for multi-tenant filtering
            limit: Maximum results to return
            
        Returns:
            List of active memberships
        
        Example:
            active = await membership_model.get_active(salon_id="salon_123")
        """
        return await self.list(
            salon_id=salon_id,
            filters=[("status", "==", "active")],
            order_by="valid_till",
            limit=limit,
        )
    
    async def get_expiring(
        self,
        salon_id: str,
        days_before: int = 15,
        limit: int = 100,
    ) -> List[Membership]:
        """Get memberships expiring soon.
        
        Args:
            salon_id: Salon ID for multi-tenant filtering
            days_before: Number of days before expiration to check
            limit: Maximum results to return
            
        Returns:
            List of memberships expiring within the threshold
        """
        today = date.today()
        expiry_threshold = today + timedelta(days=days_before)
        
        return await self.list(
            salon_id=salon_id,
            filters=[
                ("status", "==", "active"),
                ("valid_till", "<=", expiry_threshold.isoformat()),
                ("valid_till", ">=", today.isoformat()),
            ],
            order_by="valid_till",
            limit=limit,
        )
    
    async def renew_membership(
        self,
        membership_id: str,
        salon_id: str,
        new_plan_type: Optional[MembershipPlanType] = None,
        payment_id: Optional[str] = None,
    ) -> Optional[Membership]:
        """Renew a membership.
        
        Args:
            membership_id: Membership document ID
            salon_id: Salon ID for verification
            new_plan_type: Optional new plan type (defaults to current)
            payment_id: Payment ID for the renewal
            
        Returns:
            Updated membership if successful
        """
        membership = await self.get(membership_id)
        if not membership or membership.salon_id != salon_id:
            return None
        
        # Calculate new validity based on plan type
        plan_type = new_plan_type or membership.plan_type
        if isinstance(plan_type, MembershipPlanType):
            plan_type = plan_type.value
        
        if plan_type == "monthly":
            validity_days = 30
        elif plan_type == "quarterly":
            validity_days = 90
        elif plan_type == "annual":
            validity_days = 365
        else:
            validity_days = 30
        
        # Extend from current end date or today
        current_end = membership.valid_till
        if isinstance(current_end, str):
            current_end = date.fromisoformat(current_end)
        
        if current_end and current_end > date.today():
            new_valid_till = current_end + timedelta(days=validity_days)
        else:
            new_valid_till = date.today() + timedelta(days=validity_days)
        
        update_data = {
            "status": "active",
            "valid_till": new_valid_till.isoformat(),
            "plan_type": plan_type,
            "renewal_count": (membership.renewal_count or 0) + 1,
            "last_renewed_at": datetime.utcnow().isoformat(),
            "last_payment_id": payment_id,
        }
        
        return await self.update(membership_id, update_data)
    
    async def get_by_customer(
        self,
        customer_id: str,
        salon_id: str,
        active_only: bool = False,
    ) -> List[Membership]:
        """Get all memberships for a customer.
        
        Args:
            customer_id: Customer document ID
            salon_id: Salon ID for multi-tenant filtering
            active_only: If True, only return active memberships
            
        Returns:
            List of memberships for the customer
        """
        filters = [("customer_id", "==", customer_id)]
        
        if active_only:
            filters.append(("status", "==", "active"))
        
        return await self.list(
            salon_id=salon_id,
            filters=filters,
            order_by="created_at",
            order_direction="DESCENDING",
        )
    
    async def get_active_for_customer(
        self,
        customer_id: str,
        salon_id: str,
    ) -> Optional[Membership]:
        """Get active membership for a customer.
        
        Args:
            customer_id: Customer document ID
            salon_id: Salon ID for multi-tenant filtering
            
        Returns:
            Active membership if exists, None otherwise
        """
        today = date.today()
        
        memberships = await self.list(
            salon_id=salon_id,
            filters=[
                ("customer_id", "==", customer_id),
                ("status", "==", "active"),
                ("valid_till", ">=", today.isoformat()),
            ],
            limit=1,
        )
        
        return memberships[0] if memberships else None
    
    async def get_by_plan(
        self,
        plan_type: str,
        salon_id: str,
        active_only: bool = True,
        limit: int = 100,
    ) -> List[Membership]:
        """Get memberships by plan type.
        
        Args:
            plan_type: Plan type (monthly, quarterly, annual)
            salon_id: Salon ID for multi-tenant filtering
            active_only: If True, only return active memberships
            limit: Maximum results to return
            
        Returns:
            List of memberships with the plan type
        """
        filters = [("plan_type", "==", plan_type)]
        
        if active_only:
            filters.append(("status", "==", "active"))
        
        return await self.list(
            salon_id=salon_id,
            filters=filters,
            order_by="created_at",
            order_direction="DESCENDING",
            limit=limit,
        )
    
    async def update_usage(
        self,
        membership_id: str,
        amount_used: float,
        service_count: int = 1,
    ) -> Optional[Membership]:
        """Update membership usage after a service.
        
        Args:
            membership_id: Membership document ID
            amount_used: Amount deducted from membership
            service_count: Number of services used
            
        Returns:
            Updated membership if successful
        """
        try:
            doc_ref = self.collection.document(membership_id)
            
            # Use atomic increment for usage tracking
            await doc_ref.update({
                "usage.total_services_used": service_count,
                "usage.total_amount_used": amount_used,
                "usage.last_used_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow(),
            })
            
            return await self.get(membership_id)
            
        except Exception as e:
            logger.error(
                "Failed to update membership usage",
                membership_id=membership_id,
                error=str(e),
            )
            raise
    
    async def cancel_membership(
        self,
        membership_id: str,
        salon_id: str,
        reason: str,
        cancelled_by: str,
    ) -> Optional[Membership]:
        """Cancel a membership.
        
        Args:
            membership_id: Membership document ID
            salon_id: Salon ID for verification
            reason: Cancellation reason
            cancelled_by: User ID who cancelled
            
        Returns:
            Updated membership if successful
        """
        membership = await self.get(membership_id)
        if not membership or membership.salon_id != salon_id:
            return None
        
        update_data = {
            "status": "cancelled",
            "cancellation": {
                "reason": reason,
                "cancelled_by": cancelled_by,
                "cancelled_at": datetime.utcnow().isoformat(),
            },
        }
        
        return await self.update(membership_id, update_data)
    
    async def expire_memberships(
        self,
        salon_id: Optional[str] = None,
        batch_size: int = 50,
    ) -> int:
        """Mark expired memberships as expired status.
        
        Args:
            salon_id: Optional salon ID (if None, process all salons)
            batch_size: Number of memberships to process
            
        Returns:
            Number of memberships expired
        """
        today = date.today()
        
        filters = [
            ("status", "==", "active"),
            ("valid_till", "<", today.isoformat()),
        ]
        
        expired_memberships = await self.list(
            salon_id=salon_id,
            filters=filters,
            limit=batch_size,
        )
        
        count = 0
        for membership in expired_memberships:
            try:
                await self.update(membership.id, {
                    "status": "expired",
                    "expired_at": datetime.utcnow().isoformat(),
                })
                count += 1
            except Exception as e:
                logger.error(
                    "Failed to expire membership",
                    membership_id=membership.id,
                    error=str(e),
                )
        
        return count
    
    async def get_membership_stats(
        self,
        salon_id: str,
    ) -> Dict[str, Any]:
        """Get membership statistics for a salon.
        
        Args:
            salon_id: Salon ID
            
        Returns:
            Membership statistics dictionary
        """
        try:
            # Get counts by status
            active_count = await self.count(
                salon_id=salon_id,
                filters=[("status", "==", "active")],
            )
            
            expired_count = await self.count(
                salon_id=salon_id,
                filters=[("status", "==", "expired")],
            )
            
            cancelled_count = await self.count(
                salon_id=salon_id,
                filters=[("status", "==", "cancelled")],
            )
            
            # Get counts by plan type
            monthly_count = await self.count(
                salon_id=salon_id,
                filters=[("plan_type", "==", "monthly"), ("status", "==", "active")],
            )
            
            quarterly_count = await self.count(
                salon_id=salon_id,
                filters=[("plan_type", "==", "quarterly"), ("status", "==", "active")],
            )
            
            annual_count = await self.count(
                salon_id=salon_id,
                filters=[("plan_type", "==", "annual"), ("status", "==", "active")],
            )
            
            return {
                "total_active": active_count,
                "total_expired": expired_count,
                "total_cancelled": cancelled_count,
                "by_plan_type": {
                    "monthly": monthly_count,
                    "quarterly": quarterly_count,
                    "annual": annual_count,
                },
            }
            
        except Exception as e:
            logger.error(
                "Failed to get membership stats",
                salon_id=salon_id,
                error=str(e),
            )
            raise
    
    async def get_revenue_by_plan(
        self,
        salon_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Dict[str, Any]:
        """Get membership revenue by plan type.
        
        Args:
            salon_id: Salon ID for multi-tenant filtering
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Revenue breakdown by plan type
        """
        try:
            filters = []
            
            if start_date:
                filters.append(("created_at", ">=", start_date.isoformat()))
            if end_date:
                filters.append(("created_at", "<=", end_date.isoformat()))
            
            memberships = await self.list(
                salon_id=salon_id,
                filters=filters if filters else None,
                limit=500,
            )
            
            revenue_by_plan = {}
            total_revenue = 0
            
            for membership in memberships:
                plan = membership.plan_type.value if hasattr(membership.plan_type, 'value') else membership.plan_type
                amount = float(membership.amount_paid or 0)
                
                if plan not in revenue_by_plan:
                    revenue_by_plan[plan] = {"count": 0, "revenue": 0}
                
                revenue_by_plan[plan]["count"] += 1
                revenue_by_plan[plan]["revenue"] += amount
                total_revenue += amount
            
            
            return {
                "total_revenue": total_revenue,
                "by_plan": revenue_by_plan,
            }
            
        except Exception as e:
            logger.error(
                "Failed to get membership revenue",
                salon_id=salon_id,
                error=str(e),
            )
            raise
    
    async def get_new_memberships(
        self,
        salon_id: str,
        days: int = 30,
        limit: int = 100,
    ) -> List[Membership]:
        """Get recently created memberships.
        
        Args:
            salon_id: Salon ID for multi-tenant filtering
            days: Number of days to look back
            limit: Maximum results to return
            
        Returns:
            List of new memberships
        """
        threshold = datetime.utcnow() - timedelta(days=days)
        
        return await self.list(
            salon_id=salon_id,
            filters=[("created_at", ">=", threshold.isoformat())],
            order_by="created_at",
            order_direction="DESCENDING",
            limit=limit,
        )
