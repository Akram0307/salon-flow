"""Event Publisher for Autonomous Agent Events.

Publishes events to Google Cloud Pub/Sub for downstream processing.
"""
import json
from datetime import datetime
from typing import Dict, Any, Optional
import structlog

from google.cloud import pubsub_v1
from app.core.config import settings

logger = structlog.get_logger()


class EventPublisher:
    """Publishes autonomous agent events to Pub/Sub.
    
    Events are published to the 'salon-events' topic for:
    - Real-time dashboard updates
    - Analytics aggregation
    - Notification triggers
    - Audit logging
    """
    
    def __init__(self):
        self.publisher = pubsub_v1.PublisherClient()
        self.topic_path = self.publisher.topic_path(
            settings.GCP_PROJECT_ID,
            "salon-events"
        )
    
    async def publish(
        self,
        event_type: str,
        salon_id: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, str]] = None,
    ) -> str:
        """Publish an event to Pub/Sub.
        
        Args:
            event_type: Type of event (e.g., 'AUTONOMOUS_DECISION')
            salon_id: Salon ID for routing
            data: Event payload
            metadata: Optional metadata attributes
            
        Returns:
            Published message ID
        """
        event = {
            "event_type": event_type,
            "salon_id": salon_id,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data,
        }
        
        # Add metadata as attributes
        attributes = {
            "event_type": event_type,
            "salon_id": salon_id,
        }
        if metadata:
            attributes.update(metadata)
        
        # Publish asynchronously
        future = self.publisher.publish(
            self.topic_path,
            json.dumps(event).encode("utf-8"),
            **attributes
        )
        
        message_id = future.result()
        
        logger.debug(
            "event_published",
            event_type=event_type,
            salon_id=salon_id,
            message_id=message_id,
        )
        
        return message_id
    
    async def publish_decision_event(
        self,
        salon_id: str,
        decision_id: str,
        agent_name: str,
        decision_type: str,
        action: str,
        outcome: str,
        revenue_impact: Optional[float] = None,
    ) -> str:
        """Publish autonomous decision event.
        
        Args:
            salon_id: Salon ID
            decision_id: Decision document ID
            agent_name: Agent that made decision
            decision_type: Type of decision
            action: Action taken
            outcome: Decision outcome
            revenue_impact: Optional revenue impact
            
        Returns:
            Message ID
        """
        return await self.publish(
            event_type="AUTONOMOUS_DECISION",
            salon_id=salon_id,
            data={
                "decision_id": decision_id,
                "agent_name": agent_name,
                "decision_type": decision_type,
                "action": action,
                "outcome": outcome,
                "revenue_impact": revenue_impact,
            },
            metadata={
                "agent_name": agent_name,
                "decision_type": decision_type,
            },
        )
    
    async def publish_gap_event(
        self,
        salon_id: str,
        gap_id: str,
        event: str,
        staff_id: str,
        duration_minutes: int,
        potential_revenue: float,
    ) -> str:
        """Publish gap-related event.
        
        Args:
            salon_id: Salon ID
            gap_id: Gap document ID
            event: Event type (detected, filled, expired)
            staff_id: Staff ID
            duration_minutes: Gap duration
            potential_revenue: Potential revenue
            
        Returns:
            Message ID
        """
        return await self.publish(
            event_type=f"GAP_{event.upper()}",
            salon_id=salon_id,
            data={
                "gap_id": gap_id,
                "staff_id": staff_id,
                "duration_minutes": duration_minutes,
                "potential_revenue": potential_revenue,
            },
        )
    
    async def publish_outreach_event(
        self,
        salon_id: str,
        outreach_id: str,
        customer_id: str,
        channel: str,
        event: str,
        response_action: Optional[str] = None,
    ) -> str:
        """Publish outreach event.
        
        Args:
            salon_id: Salon ID
            outreach_id: Outreach document ID
            customer_id: Customer ID
            channel: Communication channel
            event: Event type (sent, delivered, responded)
            response_action: Customer response action
            
        Returns:
            Message ID
        """
        return await self.publish(
            event_type=f"OUTREACH_{event.upper()}",
            salon_id=salon_id,
            data={
                "outreach_id": outreach_id,
                "customer_id": customer_id,
                "channel": channel,
                "response_action": response_action,
            },
        )
    
    async def publish_approval_event(
        self,
        salon_id: str,
        approval_id: str,
        decision_id: str,
        event: str,
        responded_by: Optional[str] = None,
    ) -> str:
        """Publish approval workflow event.
        
        Args:
            salon_id: Salon ID
            approval_id: Approval document ID
            decision_id: Associated decision ID
            event: Event type (requested, approved, rejected, expired)
            responded_by: User who responded
            
        Returns:
            Message ID
        """
        return await self.publish(
            event_type=f"APPROVAL_{event.upper()}",
            salon_id=salon_id,
            data={
                "approval_id": approval_id,
                "decision_id": decision_id,
                "responded_by": responded_by,
            },
        )
