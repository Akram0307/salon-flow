"""Approval Workflow Service.

Manages approval requests for supervised autonomous actions.
"""
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import structlog

from app.models.autonomous import (
    ApprovalModel,
    ApprovalStatus,
    ApprovalPriority,
    AutonomousDecisionModel,
    AuditLogModel,
    AuditEventType,
    AuditSeverity,
)
from app.services.autonomous.event_publisher import EventPublisher

logger = structlog.get_logger()


class ApprovalService:
    """Manages approval workflow for autonomous agent actions.
    
    Handles:
    - Approval request creation
    - Owner notification
    - Response processing
    - Expiration handling
    """
    
    DEFAULT_EXPIRY_MINUTES = 15  # Default time for approval
    
    def __init__(self):
        self.approval_model = ApprovalModel()
        self.decision_model = AutonomousDecisionModel()
        self.audit_model = AuditLogModel()
        self.event_publisher = EventPublisher()
    
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
        """Create an approval request.
        
        Args:
            salon_id: Salon ID
            decision_id: Associated decision ID
            agent_name: Agent requesting approval
            action_type: Type of action
            action_summary: Human-readable summary
            action_details: Detailed action information
            priority: Approval priority
            expires_in_minutes: Time until expiration
            
        Returns:
            Created approval request
        """
        expiry = expires_in_minutes or self.DEFAULT_EXPIRY_MINUTES
        
        approval = await self.approval_model.create_request(
            salon_id=salon_id,
            decision_id=decision_id,
            agent_name=agent_name,
            action_type=action_type,
            action_summary=action_summary,
            action_details=action_details,
            priority=priority,
            expires_in_minutes=expiry,
        )
        
        # Log audit
        await self.audit_model.log_event(
            salon_id=salon_id,
            event_type=AuditEventType.APPROVAL_REQUESTED,
            severity=AuditSeverity.INFO,
            actor=agent_name,
            action="Approval requested",
            resource_type="approval",
            resource_id=approval["id"],
            details={
                "decision_id": decision_id,
                "action_type": action_type,
                "priority": priority.value,
            },
        )
        
        # Publish event
        await self.event_publisher.publish_approval_event(
            salon_id=salon_id,
            approval_id=approval["id"],
            decision_id=decision_id,
            event="requested",
        )
        
        logger.info(
            "approval_requested",
            salon_id=salon_id,
            approval_id=approval["id"],
            decision_id=decision_id,
            agent=agent_name,
        )
        
        return approval
    
    async def process_approval(
        self,
        approval_id: str,
        salon_id: str,
        action: str,
        user_id: str,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Process approval decision.
        
        Args:
            approval_id: Approval document ID
            salon_id: Salon ID
            action: 'approve' or 'reject'
            user_id: User making decision
            notes: Optional notes
            
        Returns:
            Updated approval record
        """
        approval = await self.approval_model.get(approval_id)
        
        if not approval or approval.get("salon_id") != salon_id:
            raise ValueError("Approval not found")
        
        if approval.get("status") != ApprovalStatus.PENDING.value:
            raise ValueError(f"Approval already {approval.get('status')}")
        
        # Check expiration
        expires_at = approval.get("expires_at", "")
        if expires_at and datetime.utcnow().isoformat() > expires_at:
            await self.approval_model.mark_expired(approval_id)
            raise ValueError("Approval has expired")
        
        # Process action
        if action == "approve":
            updated = await self.approval_model.approve(approval_id, user_id, notes)
            event_type = AuditEventType.APPROVAL_GRANTED
            event = "approved"
        else:
            updated = await self.approval_model.reject(approval_id, user_id, notes or "Rejected")
            event_type = AuditEventType.APPROVAL_REJECTED
            event = "rejected"
        
        # Update associated decision
        decision_id = approval.get("decision_id")
        if decision_id:
            await self.decision_model.update(decision_id, {
                "approval.status": event,
                "approval.approved_by" if action == "approve" else "approval.rejected_by": user_id,
                "approval.approved_at" if action == "approve" else "approval.rejected_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            })
        
        # Log audit
        await self.audit_model.log_event(
            salon_id=salon_id,
            event_type=event_type,
            severity=AuditSeverity.INFO,
            actor=user_id,
            action=f"Approval {action}d",
            resource_type="approval",
            resource_id=approval_id,
            details={
                "decision_id": decision_id,
                "notes": notes,
            },
        )
        
        # Publish event
        await self.event_publisher.publish_approval_event(
            salon_id=salon_id,
            approval_id=approval_id,
            decision_id=decision_id,
            event=event,
            responded_by=user_id,
        )
        
        logger.info(
            "approval_processed",
            approval_id=approval_id,
            action=action,
            user=user_id,
        )
        
        return updated
    
    async def get_pending_approvals(
        self,
        salon_id: str,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Get pending approval requests.
        
        Args:
            salon_id: Salon ID
            limit: Maximum records
            
        Returns:
            List of pending approvals
        """
        return await self.approval_model.get_pending_approvals(salon_id, limit)
    
    async def get_urgent_approvals(
        self,
        salon_id: str,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get urgent/high-priority approvals.
        
        Args:
            salon_id: Salon ID
            limit: Maximum records
            
        Returns:
            List of urgent approvals
        """
        return await self.approval_model.list(
            salon_id=salon_id,
            filters=[
                ("status", "==", ApprovalStatus.PENDING.value),
                ("priority", "in", [ApprovalPriority.HIGH.value, ApprovalPriority.URGENT.value]),
            ],
            order_by="created_at",
            order_direction="ASCENDING",
            limit=limit,
        )
    
    async def cleanup_expired(self, salon_id: str) -> int:
        """Mark expired approvals.
        
        Args:
            salon_id: Salon ID
            
        Returns:
            Number of expired approvals
        """
        now = datetime.utcnow().isoformat()
        
        expired = await self.approval_model.list(
            salon_id=salon_id,
            filters=[
                ("status", "==", ApprovalStatus.PENDING.value),
                ("expires_at", "<", now),
            ],
            limit=100,
        )
        
        for approval in expired:
            await self.approval_model.mark_expired(approval["id"])
            
            # Update associated decision
            decision_id = approval.get("decision_id")
            if decision_id:
                await self.decision_model.update(decision_id, {
                    "approval.status": "expired",
                    "outcome.status": "expired",
                    "updated_at": datetime.utcnow().isoformat(),
                })
            
            # Log audit
            await self.audit_model.log_event(
                salon_id=salon_id,
                event_type=AuditEventType.APPROVAL_EXPIRED,
                severity=AuditSeverity.WARNING,
                actor="system",
                action="Approval expired",
                resource_type="approval",
                resource_id=approval["id"],
            )
        
        if expired:
            logger.info(
                "approval_expired_cleanup",
                salon_id=salon_id,
                count=len(expired),
            )
        
        return len(expired)
    
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
            Approval statistics
        """
        return await self.approval_model.get_approval_stats(salon_id, days)
