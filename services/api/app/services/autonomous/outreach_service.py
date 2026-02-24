"""Outreach Coordination Service.

Manages customer outreach via WhatsApp/SMS for autonomous agents.
"""
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import structlog

from app.models.autonomous import (
    OutreachModel,
    OutreachStatus,
    OutreachType,
    OutreachChannel,
    AutonomousDecisionModel,
    AgentStateModel,
)
from app.services.autonomous.event_publisher import EventPublisher

logger = structlog.get_logger()


class OutreachService:
    """Coordinates customer outreach operations.
    
    Handles:
    - Message composition and personalization
    - Rate limiting and cooldowns
    - Response tracking
    - Conversion attribution
    """
    
    # Rate limits per salon
    HOURLY_LIMIT = 50
    DAILY_LIMIT = 200
    COOLDOWN_HOURS = 1  # Minimum hours between outreach to same customer
    
    def __init__(self):
        self.outreach_model = OutreachModel()
        self.decision_model = AutonomousDecisionModel()
        self.agent_model = AgentStateModel()
        self.event_publisher = EventPublisher()
    
    async def can_send_outreach(
        self,
        salon_id: str,
        customer_phone: str,
    ) -> Dict[str, Any]:
        """Check if outreach can be sent to a customer.
        
        Args:
            salon_id: Salon ID
            customer_phone: Customer phone number
            
        Returns:
            Dict with 'allowed' boolean and reason if not allowed
        """
        # Check for recent outreach to same phone
        recent = await self.outreach_model.get_recent_by_phone(
            customer_phone, salon_id, hours=self.COOLDOWN_HOURS
        )
        
        if recent:
            return {
                "allowed": False,
                "reason": "cooldown_active",
                "last_outreach": recent.get("created_at"),
                "cooldown_until": self._calculate_cooldown_end(recent),
            }
        
        # Check daily limit
        today_count = await self._get_today_count(salon_id)
        if today_count >= self.DAILY_LIMIT:
            return {
                "allowed": False,
                "reason": "daily_limit_exceeded",
                "current": today_count,
                "limit": self.DAILY_LIMIT,
            }
        
        return {"allowed": True}
    
    def _calculate_cooldown_end(self, outreach: Dict) -> str:
        """Calculate when cooldown ends."""
        created = outreach.get("created_at", "")
        if created:
            dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
            end = dt + timedelta(hours=self.COOLDOWN_HOURS)
            return end.isoformat()
        return ""
    
    async def _get_today_count(self, salon_id: str) -> int:
        """Get today's outreach count for salon."""
        from datetime import date
        today = date.today().isoformat()
        
        outreach_list = await self.outreach_model.list(
            salon_id=salon_id,
            filters=[("created_at", ">=", today)],
            limit=1000,
        )
        return len(outreach_list)
    
    async def create_outreach(
        self,
        salon_id: str,
        customer_id: str,
        customer_name: str,
        customer_phone: str,
        outreach_type: OutreachType,
        channel: OutreachChannel,
        message: str,
        trigger_id: Optional[str] = None,
        trigger_type: Optional[str] = None,
        offer_details: Optional[Dict] = None,
        expires_in_minutes: int = 15,
    ) -> Dict[str, Any]:
        """Create and prepare outreach for sending.
        
        Args:
            salon_id: Salon ID
            customer_id: Customer ID
            customer_name: Customer name
            customer_phone: Customer phone
            outreach_type: Type of outreach
            channel: Communication channel
            message: Message content
            trigger_id: Triggering entity ID
            trigger_type: Trigger type
            offer_details: Offer details if applicable
            expires_in_minutes: Response deadline
            
        Returns:
            Created outreach record
        """
        # Check if can send
        check = await self.can_send_outreach(salon_id, customer_phone)
        if not check["allowed"]:
            raise ValueError(f"Cannot send outreach: {check['reason']}")
        
        # Create outreach record
        outreach = await self.outreach_model.create_outreach(
            salon_id=salon_id,
            customer_id=customer_id,
            customer_name=customer_name,
            customer_phone=customer_phone,
            outreach_type=outreach_type,
            channel=channel,
            message=message,
            trigger_id=trigger_id,
            trigger_type=trigger_type,
            offer_details=offer_details or {},
            expires_in_minutes=expires_in_minutes,
        )
        
        logger.info(
            "outreach_created",
            salon_id=salon_id,
            outreach_id=outreach["id"],
            customer=customer_id,
            type=outreach_type.value,
        )
        
        return outreach
    
    async def process_delivery_status(
        self,
        outreach_id: str,
        status: OutreachStatus,
        message_id: Optional[str] = None,
        error: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Process delivery status update from webhook.
        
        Args:
            outreach_id: Outreach document ID
            status: New status
            message_id: Provider message ID
            error: Error message if failed
            
        Returns:
            Updated outreach record
        """
        outreach = await self.outreach_model.get(outreach_id)
        if not outreach:
            raise ValueError(f"Outreach {outreach_id} not found")
        
        if status == OutreachStatus.SENT and message_id:
            updated = await self.outreach_model.mark_sent(outreach_id, message_id)
        elif status == OutreachStatus.DELIVERED:
            updated = await self.outreach_model.mark_delivered(outreach_id)
        elif status == OutreachStatus.READ:
            updated = await self.outreach_model.mark_read(outreach_id)
        elif status == OutreachStatus.FAILED:
            updated = await self.outreach_model.mark_failed(outreach_id, error or "Unknown error")
        else:
            updated = await self.outreach_model.update(outreach_id, {
                "status": status.value,
                "updated_at": datetime.utcnow().isoformat(),
            })
        
        # Publish event
        await self.event_publisher.publish_outreach_event(
            salon_id=outreach["salon_id"],
            outreach_id=outreach_id,
            customer_id=outreach["customer_id"],
            channel=outreach["channel"],
            event=status.value,
        )
        
        return updated
    
    async def process_customer_response(
        self,
        outreach_id: str,
        action: str,
        booking_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Process customer response to outreach.
        
        Args:
            outreach_id: Outreach document ID
            action: Customer action (accept, decline, book)
            booking_id: Booking ID if created
            
        Returns:
            Updated outreach record
        """
        outreach = await self.outreach_model.get(outreach_id)
        if not outreach:
            raise ValueError(f"Outreach {outreach_id} not found")
        
        # Record response
        updated = await self.outreach_model.record_response(
            outreach_id=outreach_id,
            action=action,
            booking_id=booking_id,
        )
        
        # Update associated decision if exists
        if outreach.get("trigger_id") and outreach.get("trigger_type") == "gap":
            from app.services.autonomous.gap_fill_service import GapFillService
            gap_service = GapFillService()
            
            if action == "book" and booking_id:
                await gap_service.process_gap_filled(
                    salon_id=outreach["salon_id"],
                    gap_id=outreach["trigger_id"],
                    booking_id=booking_id,
                    customer_id=outreach["customer_id"],
                )
        
        # Publish event
        await self.event_publisher.publish_outreach_event(
            salon_id=outreach["salon_id"],
            outreach_id=outreach_id,
            customer_id=outreach["customer_id"],
            channel=outreach["channel"],
            event="responded",
            response_action=action,
        )
        
        logger.info(
            "outreach_response",
            outreach_id=outreach_id,
            action=action,
            booking_id=booking_id,
        )
        
        return updated
    
    async def get_pending_outreach(
        self,
        salon_id: str,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get pending outreach that needs to be sent.
        
        Args:
            salon_id: Salon ID
            limit: Maximum records
            
        Returns:
            List of pending outreach records
        """
        return await self.outreach_model.list(
            salon_id=salon_id,
            filters=[("status", "==", OutreachStatus.PENDING.value)],
            order_by="created_at",
            order_direction="ASCENDING",
            limit=limit,
        )
    
    async def get_expired_outreach(
        self,
        salon_id: str,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get expired outreach that needs cleanup.
        
        Args:
            salon_id: Salon ID
            limit: Maximum records
            
        Returns:
            List of expired outreach records
        """
        now = datetime.utcnow().isoformat()
        
        return await self.outreach_model.list(
            salon_id=salon_id,
            filters=[
                ("status", "==", OutreachStatus.PENDING.value),
                ("expires_at", "<", now),
            ],
            limit=limit,
        )
    
    async def cleanup_expired(self, salon_id: str) -> int:
        """Mark expired outreach as expired.
        
        Args:
            salon_id: Salon ID
            
        Returns:
            Number of expired records
        """
        expired = await self.get_expired_outreach(salon_id)
        
        for outreach in expired:
            await self.outreach_model.update(outreach["id"], {
                "status": OutreachStatus.EXPIRED.value,
                "updated_at": datetime.utcnow().isoformat(),
            })
        
        if expired:
            logger.info(
                "outreach_expired_cleanup",
                salon_id=salon_id,
                count=len(expired),
            )
        
        return len(expired)
