"""Autonomous Decision Firestore Model.

Handles all database operations for autonomous agent decisions.
"""
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from enum import Enum

from google.cloud.firestore_v1.base_query import FieldFilter
import structlog

from app.models.base import FirestoreBase
from app.schemas.base import PaginatedResponse

logger = structlog.get_logger()


class DecisionType(str, Enum):
    """Types of autonomous decisions."""
    GAP_FILL = "gap_fill"
    NO_SHOW_PREVENTION = "no_show_prevention"
    WAITLIST_PROMOTION = "waitlist_promotion"
    DISCOUNT_OFFER = "discount_offer"
    DYNAMIC_PRICING = "dynamic_pricing"


class AutonomyLevel(str, Enum):
    """Autonomy levels for agent actions."""
    FULL_AUTO = "full_auto"
    SUPERVISED = "supervised"
    MANUAL_ONLY = "manual_only"


class DecisionStatus(str, Enum):
    """Status of autonomous decisions."""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    EXPIRED = "expired"
    REJECTED = "rejected"


class AutonomousDecisionModel(FirestoreBase):
    """Model for autonomous decision operations.
    
    Provides CRUD operations and specialized queries for tracking
    all autonomous decisions made by AI agents.
    
    Attributes:
        collection_name: Firestore collection name ('autonomous_decisions')
    """
    
    collection_name = "autonomous_decisions"
    
    async def get_by_decision_type(
        self,
        decision_type: DecisionType,
        salon_id: str,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get decisions by type.
        
        Args:
            decision_type: Type of decision
            salon_id: Salon ID for multi-tenant filtering
            date_from: Optional start date filter
            date_to: Optional end date filter
            limit: Maximum results to return
            
        Returns:
            List of decisions
        """
        filters = [("decision_type", "==", decision_type.value)]
        
        if date_from:
            filters.append(("created_at", ">=", date_from.isoformat()))
        if date_to:
            filters.append(("created_at", "<=", date_to.isoformat()))
        
        return await self.list(
            salon_id=salon_id,
            filters=filters,
            order_by="created_at",
            order_direction="DESCENDING",
            limit=limit,
        )
    
    async def get_pending_decisions(
        self,
        salon_id: str,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get all pending decisions awaiting outcome.
        
        Args:
            salon_id: Salon ID for multi-tenant filtering
            limit: Maximum results to return
            
        Returns:
            List of pending decisions
        """
        return await self.list(
            salon_id=salon_id,
            filters=[("outcome.status", "==", "pending")],
            order_by="created_at",
            order_direction="DESCENDING",
            limit=limit,
        )
    
    async def get_by_customer(
        self,
        customer_id: str,
        salon_id: str,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get all decisions for a customer.
        
        Args:
            customer_id: Customer document ID
            salon_id: Salon ID for multi-tenant filtering
            limit: Maximum results to return
            
        Returns:
            List of decisions for the customer
        """
        return await self.list(
            salon_id=salon_id,
            filters=[("context.customer_id", "==", customer_id)],
            order_by="created_at",
            order_direction="DESCENDING",
            limit=limit,
        )
    
    async def get_by_gap(
        self,
        gap_id: str,
        salon_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Get decision for a specific gap.
        
        Args:
            gap_id: Gap document ID
            salon_id: Salon ID for multi-tenant filtering
            
        Returns:
            Decision if found, None otherwise
        """
        results = await self.list(
            salon_id=salon_id,
            filters=[("context.trigger_id", "==", gap_id)],
            limit=1,
        )
        return results[0] if results else None
    
    async def update_outcome(
        self,
        decision_id: str,
        status: DecisionStatus,
        result: Optional[str] = None,
        booking_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Update decision outcome.
        
        Args:
            decision_id: Decision document ID
            status: New outcome status
            result: Outcome result description
            booking_id: Booking ID if created
            
        Returns:
            Updated decision if successful
        """
        update_data = {
            "outcome.status": status.value,
            "outcome.result": result,
            "outcome.completed_at": datetime.utcnow().isoformat(),
            "outcome.booking_created_id": booking_id,
            "updated_at": datetime.utcnow().isoformat(),
        }
        
        return await self.update(decision_id, update_data)
    
    async def get_daily_stats(
        self,
        salon_id: str,
        target_date: Optional[date] = None,
    ) -> Dict[str, Any]:
        """Get decision statistics for a day.
        
        Args:
            salon_id: Salon ID for multi-tenant filtering
            target_date: Date to query (defaults to today)
            
        Returns:
            Statistics summary
        """
        target_date = target_date or date.today()
        start = datetime.combine(target_date, datetime.min.time())
        end = start + timedelta(days=1)
        
        decisions = await self.list(
            salon_id=salon_id,
            filters=[
                ("created_at", ">=", start.isoformat()),
                ("created_at", "<", end.isoformat()),
            ],
            limit=500,
        )
        
        stats = {
            "date": target_date.isoformat(),
            "total": len(decisions),
            "by_type": {},
            "by_status": {},
            "revenue": {
                "potential": 0,
                "actual": 0,
            },
        }
        
        for decision in decisions:
            # By type
            dec_type = decision.get("decision_type", "unknown")
            stats["by_type"][dec_type] = stats["by_type"].get(dec_type, 0) + 1
            
            # By status
            status = decision.get("outcome", {}).get("status", "unknown")
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
            
            # Revenue
            revenue = decision.get("revenue_impact", {})
            stats["revenue"]["potential"] += revenue.get("potential", 0)
            if status == "success":
                stats["revenue"]["actual"] += revenue.get("actual", 0)
        
        return stats
    
    async def get_success_rate(
        self,
        salon_id: str,
        days: int = 7,
    ) -> Dict[str, Any]:
        """Calculate success rate over a period.
        
        Args:
            salon_id: Salon ID for multi-tenant filtering
            days: Number of days to analyze
            
        Returns:
            Success rate metrics
        """
        start_date = date.today() - timedelta(days=days)
        
        decisions = await self.list(
            salon_id=salon_id,
            filters=[
                ("created_at", ">=", start_date.isoformat()),
            ],
            limit=1000,
        )
        
        total = len(decisions)
        if total == 0:
            return {"rate": 0, "total": 0, "successful": 0}
        
        successful = sum(
            1 for d in decisions
            if d.get("outcome", {}).get("status") == "success"
        )
        
        return {
            "rate": successful / total,
            "total": total,
            "successful": successful,
            "period_days": days,
        }
    
    async def create_decision(
        self,
        salon_id: str,
        agent_name: str,
        decision_type: DecisionType,
        autonomy_level: AutonomyLevel,
        context: Dict[str, Any],
        action_taken: str,
        action_details: Dict[str, Any],
        revenue_impact: Dict[str, Any],
        approval_required: bool = False,
    ) -> Dict[str, Any]:
        """Create a new autonomous decision record.
        
        Args:
            salon_id: Salon ID
            agent_name: Name of the agent making decision
            decision_type: Type of decision
            autonomy_level: Level of autonomy
            context: Decision context
            action_taken: Action that was taken
            action_details: Details of the action
            revenue_impact: Financial impact
            approval_required: Whether approval was required
            
        Returns:
            Created decision
        """
        now = datetime.utcnow()
        
        decision_data = {
            "salon_id": salon_id,
            "agent_name": agent_name,
            "decision_type": decision_type.value,
            "autonomy_level": autonomy_level.value,
            "context": context,
            "action_taken": action_taken,
            "action_details": action_details,
            "revenue_impact": revenue_impact,
            "approval": {
                "required": approval_required,
                "status": "pending" if approval_required else "not_required",
            },
            "outcome": {
                "status": "pending",
                "result": None,
                "completed_at": None,
                "booking_created_id": None,
            },
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "expires_at": (now + timedelta(minutes=15)).isoformat(),
        }
        
        return await self.create(decision_data)
