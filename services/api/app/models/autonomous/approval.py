"""Approval Workflow Firestore Model.

Manages approval requests for supervised autonomous actions.
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from enum import Enum

import structlog

from app.models.base import FirestoreBase

logger = structlog.get_logger()


class ApprovalStatus(str, Enum):
    """Status of approval requests."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class ApprovalPriority(str, Enum):
    """Priority levels for approval requests."""
    LOW = "low"  # 30 min expiry
    MEDIUM = "medium"  # 15 min expiry
    HIGH = "high"  # 5 min expiry
    URGENT = "urgent"  # 2 min expiry


class ApprovalModel(FirestoreBase):
    """Model for approval workflow operations.
    
    Handles approval requests for autonomous actions that require
    human oversight before execution.
    """
    
    collection_name = "approval_requests"
    
    async def get_pending_approvals(
        self,
        salon_id: str,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Get all pending approval requests.
        
        Args:
            salon_id: Salon ID
            limit: Maximum results
            
        Returns:
            List of pending approvals
        """
        return await self.list(
            salon_id=salon_id,
            filters=[("status", "==", ApprovalStatus.PENDING.value)],
            order_by="created_at",
            order_direction="ASCENDING",  # Oldest first
            limit=limit,
        )
    
    async def get_by_decision(
        self,
        decision_id: str,
        salon_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Get approval for a specific decision.
        
        Args:
            decision_id: Decision document ID
            salon_id: Salon ID
            
        Returns:
            Approval if found
        """
        results = await self.list(
            salon_id=salon_id,
            filters=[("decision_id", "==", decision_id)],
            limit=1,
        )
        return results[0] if results else None
    
    async def create_approval_request(
        self,
        salon_id: str,
        decision_id: str,
        agent_name: str,
        action_type: str,
        action_summary: str,
        action_details: Dict[str, Any],
        priority: ApprovalPriority = ApprovalPriority.MEDIUM,
        expires_in_minutes: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Create a new approval request.
        
        Args:
            salon_id: Salon ID
            decision_id: Associated decision ID
            agent_name: Agent requesting approval
            action_type: Type of action
            action_summary: Human-readable summary
            action_details: Full action details
            priority: Priority level
            expires_in_minutes: Custom expiry time
            
        Returns:
            Created approval request
        """
        now = datetime.utcnow()
        
        # Set expiry based on priority
        expiry_minutes = expires_in_minutes or {
            ApprovalPriority.LOW: 30,
            ApprovalPriority.MEDIUM: 15,
            ApprovalPriority.HIGH: 5,
            ApprovalPriority.URGENT: 2,
        }.get(priority, 15)
        
        approval_data = {
            "salon_id": salon_id,
            "decision_id": decision_id,
            "agent_name": agent_name,
            "action_type": action_type,
            "action_summary": action_summary,
            "action_details": action_details,
            "priority": priority.value,
            "status": ApprovalStatus.PENDING.value,
            "expires_at": (now + timedelta(minutes=expiry_minutes)).isoformat(),
            "notifications_sent": {
                "whatsapp": False,
                "push": False,
                "email": False,
            },
            "response": {
                "action": None,
                "responded_by": None,
                "responded_at": None,
                "notes": None,
            },
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
        }
        
        return await self.create(approval_data)
    
    async def approve(
        self,
        approval_id: str,
        responded_by: str,
        notes: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Approve a request.
        
        Args:
            approval_id: Approval document ID
            responded_by: User ID who approved
            notes: Optional notes
            
        Returns:
            Updated approval
        """
        now = datetime.utcnow()
        
        update_data = {
            "status": ApprovalStatus.APPROVED.value,
            "response": {
                "action": "approved",
                "responded_by": responded_by,
                "responded_at": now.isoformat(),
                "notes": notes,
            },
            "updated_at": now.isoformat(),
        }
        
        return await self.update(approval_id, update_data)
    
    async def reject(
        self,
        approval_id: str,
        responded_by: str,
        reason: str,
    ) -> Optional[Dict[str, Any]]:
        """Reject a request.
        
        Args:
            approval_id: Approval document ID
            responded_by: User ID who rejected
            reason: Rejection reason
            
        Returns:
            Updated approval
        """
        now = datetime.utcnow()
        
        update_data = {
            "status": ApprovalStatus.REJECTED.value,
            "response": {
                "action": "rejected",
                "responded_by": responded_by,
                "responded_at": now.isoformat(),
                "notes": reason,
            },
            "updated_at": now.isoformat(),
        }
        
        return await self.update(approval_id, update_data)
    
    async def mark_expired(
        self,
        approval_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Mark an approval as expired.
        
        Args:
            approval_id: Approval document ID
            
        Returns:
            Updated approval
        """
        now = datetime.utcnow()
        
        update_data = {
            "status": ApprovalStatus.EXPIRED.value,
            "response": {
                "action": "expired",
                "responded_by": None,
                "responded_at": now.isoformat(),
                "notes": "No response received within time limit",
            },
            "updated_at": now.isoformat(),
        }
        
        return await self.update(approval_id, update_data)
    
    async def get_expired_approvals(
        self,
        salon_id: str,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get approvals that have expired but not marked.
        
        Args:
            salon_id: Salon ID
            limit: Maximum results
            
        Returns:
            List of expired approvals
        """
        now = datetime.utcnow()
        
        return await self.list(
            salon_id=salon_id,
            filters=[
                ("status", "==", ApprovalStatus.PENDING.value),
                ("expires_at", "<", now.isoformat()),
            ],
            limit=limit,
        )
    
    async def mark_notification_sent(
        self,
        approval_id: str,
        channel: str,
    ) -> bool:
        """Mark that a notification was sent.
        
        Args:
            approval_id: Approval document ID
            channel: Notification channel (whatsapp, push, email)
            
        Returns:
            True if updated
        """
        update_data = {
            f"notifications_sent.{channel}": True,
            "updated_at": datetime.utcnow().isoformat(),
        }
        
        result = await self.update(approval_id, update_data)
        return result is not None
    
    async def get_approval_stats(
        self,
        salon_id: str,
        days: int = 7,
    ) -> Dict[str, Any]:
        """Get approval statistics.
        
        Args:
            salon_id: Salon ID
            days: Number of days to analyze
            
        Returns:
            Statistics summary
        """
        from datetime import date, timedelta
        
        start_date = date.today() - timedelta(days=days)
        
        approvals = await self.list(
            salon_id=salon_id,
            filters=[
                ("created_at", ">=", start_date.isoformat()),
            ],
            limit=500,
        )
        
        stats = {
            "total": len(approvals),
            "by_status": {},
            "by_priority": {},
            "avg_response_time_seconds": 0,
            "approval_rate": 0,
        }
        
        response_times = []
        approved_count = 0
        
        for approval in approvals:
            # By status
            status = approval.get("status", "unknown")
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
            
            # By priority
            priority = approval.get("priority", "unknown")
            stats["by_priority"][priority] = stats["by_priority"].get(priority, 0) + 1
            
            # Response time
            response = approval.get("response", {})
            if response.get("responded_at") and approval.get("created_at"):
                created = datetime.fromisoformat(approval["created_at"])
                responded = datetime.fromisoformat(response["responded_at"])
                response_times.append((responded - created).total_seconds())
            
            if status == ApprovalStatus.APPROVED.value:
                approved_count += 1
        
        if response_times:
            stats["avg_response_time_seconds"] = sum(response_times) / len(response_times)
        
        total_decided = stats["by_status"].get(ApprovalStatus.APPROVED.value, 0) + \
                       stats["by_status"].get(ApprovalStatus.REJECTED.value, 0)
        if total_decided > 0:
            stats["approval_rate"] = approved_count / total_decided
        
        return stats
