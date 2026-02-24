"""Audit Log Firestore Model.

Comprehensive audit trail for all autonomous agent actions.
"""
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from enum import Enum

import structlog

from app.models.base import FirestoreBase
from app.schemas.base import PaginatedResponse

logger = structlog.get_logger()


class AuditEventType(str, Enum):
    """Types of audit events."""
    DECISION_MADE = "decision_made"
    ACTION_EXECUTED = "action_executed"
    APPROVAL_REQUESTED = "approval_requested"
    APPROVAL_GRANTED = "approval_granted"
    APPROVAL_REJECTED = "approval_rejected"
    CIRCUIT_BREAKER_TRIGGERED = "circuit_breaker_triggered"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    ERROR_OCCURRED = "error_occurred"
    CONFIG_CHANGED = "config_changed"
    MANUAL_OVERRIDE = "manual_override"


class AuditSeverity(str, Enum):
    """Severity levels for audit events."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AuditLogModel(FirestoreBase):
    """Model for audit log operations.
    
    Provides comprehensive audit trail for compliance, debugging,
    and analytics purposes.
    """
    
    collection_name = "audit_logs"
    
    async def log_event(
        self,
        salon_id: str,
        event_type: AuditEventType,
        severity: AuditSeverity,
        actor: str,
        action: str,
        resource_type: str,
        resource_id: Optional[str],
        details: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Log an audit event.
        
        Args:
            salon_id: Salon ID
            event_type: Type of event
            severity: Severity level
            actor: Who performed the action (agent name or user ID)
            action: Action performed
            resource_type: Type of resource affected
            resource_id: ID of resource affected
            details: Event details
            metadata: Optional additional metadata
            
        Returns:
            Created audit log entry
        """
        now = datetime.utcnow()
        
        audit_entry = {
            "salon_id": salon_id,
            "event_type": event_type.value,
            "severity": severity.value,
            "timestamp": now.isoformat(),
            "actor": {
                "type": "agent" if not actor.startswith("user_") else "user",
                "id": actor,
            },
            "action": action,
            "resource": {
                "type": resource_type,
                "id": resource_id,
            },
            "details": details,
            "metadata": metadata or {},
            "trace_id": metadata.get("trace_id") if metadata else None,
            "created_at": now.isoformat(),
        }
        
        return await self.create(audit_entry)
    
    async def get_by_resource(
        self,
        resource_type: str,
        resource_id: str,
        salon_id: str,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get audit logs for a specific resource.
        
        Args:
            resource_type: Type of resource
            resource_id: Resource ID
            salon_id: Salon ID
            limit: Maximum results
            
        Returns:
            List of audit entries
        """
        return await self.list(
            salon_id=salon_id,
            filters=[
                ("resource.type", "==", resource_type),
                ("resource.id", "==", resource_id),
            ],
            order_by="timestamp",
            order_direction="DESCENDING",
            limit=limit,
        )
    
    async def get_by_actor(
        self,
        actor_id: str,
        salon_id: str,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get audit logs by actor.
        
        Args:
            actor_id: Actor ID (agent name or user ID)
            salon_id: Salon ID
            limit: Maximum results
            
        Returns:
            List of audit entries
        """
        return await self.list(
            salon_id=salon_id,
            filters=[("actor.id", "==", actor_id)],
            order_by="timestamp",
            order_direction="DESCENDING",
            limit=limit,
        )
    
    async def get_by_event_type(
        self,
        event_type: AuditEventType,
        salon_id: str,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get audit logs by event type.
        
        Args:
            event_type: Type of event
            salon_id: Salon ID
            date_from: Optional start date
            date_to: Optional end date
            limit: Maximum results
            
        Returns:
            List of audit entries
        """
        filters = [("event_type", "==", event_type.value)]
        
        if date_from:
            filters.append(("timestamp", ">=", date_from.isoformat()))
        if date_to:
            filters.append(("timestamp", "<=", date_to.isoformat()))
        
        return await self.list(
            salon_id=salon_id,
            filters=filters,
            order_by="timestamp",
            order_direction="DESCENDING",
            limit=limit,
        )
    
    async def get_errors(
        self,
        salon_id: str,
        hours: int = 24,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get recent error logs.
        
        Args:
            salon_id: Salon ID
            hours: Hours to look back
            limit: Maximum results
            
        Returns:
            List of error entries
        """
        start_time = datetime.utcnow() - timedelta(hours=hours)
        
        return await self.list(
            salon_id=salon_id,
            filters=[
                ("severity", "in", [AuditSeverity.ERROR.value, AuditSeverity.CRITICAL.value]),
                ("timestamp", ">=", start_time.isoformat()),
            ],
            order_by="timestamp",
            order_direction="DESCENDING",
            limit=limit,
        )
    
    async def get_daily_summary(
        self,
        salon_id: str,
        target_date: Optional[date] = None,
    ) -> Dict[str, Any]:
        """Get daily audit summary.
        
        Args:
            salon_id: Salon ID
            target_date: Date to summarize
            
        Returns:
            Daily summary statistics
        """
        target_date = target_date or date.today()
        start = datetime.combine(target_date, datetime.min.time())
        end = start + timedelta(days=1)
        
        logs = await self.list(
            salon_id=salon_id,
            filters=[
                ("timestamp", ">=", start.isoformat()),
                ("timestamp", "<", end.isoformat()),
            ],
            limit=1000,
        )
        
        summary = {
            "date": target_date.isoformat(),
            "total_events": len(logs),
            "by_event_type": {},
            "by_severity": {},
            "by_actor": {},
            "errors": [],
        }
        
        for log in logs:
            # By event type
            event_type = log.get("event_type", "unknown")
            summary["by_event_type"][event_type] = summary["by_event_type"].get(event_type, 0) + 1
            
            # By severity
            severity = log.get("severity", "unknown")
            summary["by_severity"][severity] = summary["by_severity"].get(severity, 0) + 1
            
            # By actor
            actor = log.get("actor", {}).get("id", "unknown")
            summary["by_actor"][actor] = summary["by_actor"].get(actor, 0) + 1
            
            # Collect errors
            if severity in [AuditSeverity.ERROR.value, AuditSeverity.CRITICAL.value]:
                summary["errors"].append({
                    "timestamp": log.get("timestamp"),
                    "event_type": event_type,
                    "action": log.get("action"),
                    "details": log.get("details"),
                })
        
        return summary
    
    async def search(
        self,
        salon_id: str,
        query: Optional[str] = None,
        event_types: Optional[List[str]] = None,
        severities: Optional[List[str]] = None,
        actors: Optional[List[str]] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Search audit logs with filters.
        
        Args:
            salon_id: Salon ID
            query: Text search query
            event_types: Filter by event types
            severities: Filter by severities
            actors: Filter by actors
            date_from: Start date
            date_to: End date
            limit: Maximum results
            
        Returns:
            List of matching audit entries
        """
        filters = []
        
        if event_types:
            filters.append(("event_type", "in", event_types))
        if severities:
            filters.append(("severity", "in", severities))
        if date_from:
            filters.append(("timestamp", ">=", date_from.isoformat()))
        if date_to:
            filters.append(("timestamp", "<=", date_to.isoformat()))
        
        results = await self.list(
            salon_id=salon_id,
            filters=filters,
            order_by="timestamp",
            order_direction="DESCENDING",
            limit=limit,
        )
        
        # Text search in memory (Firestore doesn't support full-text)
        if query and results:
            query_lower = query.lower()
            results = [
                r for r in results
                if query_lower in r.get("action", "").lower() or
                   query_lower in str(r.get("details", "")).lower()
            ]
        
        # Actor filter in memory
        if actors and results:
            results = [r for r in results if r.get("actor", {}).get("id") in actors]
        
        return results
