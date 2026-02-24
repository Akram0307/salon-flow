"""Outreach Tracking Firestore Model.

Manages customer outreach attempts and responses.
"""
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from enum import Enum

import structlog

from app.models.base import FirestoreBase

logger = structlog.get_logger()


class OutreachChannel(str, Enum):
    """Communication channels for outreach."""
    WHATSAPP = "whatsapp"
    SMS = "sms"
    PUSH = "push"
    EMAIL = "email"


class OutreachStatus(str, Enum):
    """Status of outreach attempts."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    RESPONDED = "responded"
    FAILED = "failed"
    EXPIRED = "expired"


class OutreachType(str, Enum):
    """Types of outreach."""
    GAP_FILL = "gap_fill"
    NO_SHOW_PREVENTION = "no_show_prevention"
    WAITLIST_PROMOTION = "waitlist_promotion"
    DISCOUNT_OFFER = "discount_offer"
    RETENTION = "retention"
    REBOOKING = "rebooking"


class OutreachModel(FirestoreBase):
    """Model for outreach tracking operations.
    
    Tracks all customer outreach attempts, responses,
    and conversion metrics.
    """
    
    collection_name = "outreach_attempts"
    
    async def get_pending_outreach(
        self,
        salon_id: str,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get pending outreach attempts.
        
        Args:
            salon_id: Salon ID
            limit: Maximum results
            
        Returns:
            List of pending outreach
        """
        return await self.list(
            salon_id=salon_id,
            filters=[("status", "==", OutreachStatus.PENDING.value)],
            order_by="created_at",
            order_direction="ASCENDING",
            limit=limit,
        )
    
    async def get_by_customer(
        self,
        customer_id: str,
        salon_id: str,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Get outreach history for a customer.
        
        Args:
            customer_id: Customer document ID
            salon_id: Salon ID
            limit: Maximum results
            
        Returns:
            List of outreach attempts
        """
        return await self.list(
            salon_id=salon_id,
            filters=[("customer_id", "==", customer_id)],
            order_by="created_at",
            order_direction="DESCENDING",
            limit=limit,
        )
    
    async def get_by_gap(
        self,
        gap_id: str,
        salon_id: str,
    ) -> List[Dict[str, Any]]:
        """Get outreach for a specific gap.
        
        Args:
            gap_id: Gap document ID
            salon_id: Salon ID
            
        Returns:
            List of outreach attempts
        """
        return await self.list(
            salon_id=salon_id,
            filters=[("trigger_id", "==", gap_id)],
            limit=10,
        )
    
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
        offer_details: Optional[Dict[str, Any]] = None,
        expires_in_minutes: int = 15,
    ) -> Dict[str, Any]:
        """Create a new outreach attempt.
        
        Args:
            salon_id: Salon ID
            customer_id: Customer document ID
            customer_name: Customer name
            customer_phone: Customer phone number
            outreach_type: Type of outreach
            channel: Communication channel
            message: Message content
            trigger_id: ID of trigger (gap, waitlist, etc.)
            trigger_type: Type of trigger
            offer_details: Optional offer/discount details
            expires_in_minutes: Time until offer expires
            
        Returns:
            Created outreach
        """
        now = datetime.utcnow()
        
        outreach_data = {
            "salon_id": salon_id,
            "customer_id": customer_id,
            "customer_name": customer_name,
            "customer_phone": customer_phone,
            "outreach_type": outreach_type.value,
            "channel": channel.value,
            "status": OutreachStatus.PENDING.value,
            "message": message,
            "trigger_id": trigger_id,
            "trigger_type": trigger_type,
            "offer_details": offer_details or {},
            "expires_at": (now + timedelta(minutes=expires_in_minutes)).isoformat(),
            "attempts": 0,
            "last_attempt_at": None,
            "response": {
                "received": False,
                "action": None,
                "responded_at": None,
                "booking_id": None,
            },
            "delivery": {
                "message_id": None,
                "sent_at": None,
                "delivered_at": None,
                "read_at": None,
                "error": None,
            },
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
        }
        
        return await self.create(outreach_data)
    
    async def mark_sent(
        self,
        outreach_id: str,
        message_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Mark outreach as sent.
        
        Args:
            outreach_id: Outreach document ID
            message_id: Provider message ID
            
        Returns:
            Updated outreach
        """
        now = datetime.utcnow()
        
        update_data = {
            "status": OutreachStatus.SENT.value,
            "delivery.message_id": message_id,
            "delivery.sent_at": now.isoformat(),
            "attempts": 1,
            "last_attempt_at": now.isoformat(),
            "updated_at": now.isoformat(),
        }
        
        return await self.update(outreach_id, update_data)
    
    async def mark_delivered(
        self,
        outreach_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Mark outreach as delivered.
        
        Args:
            outreach_id: Outreach document ID
            
        Returns:
            Updated outreach
        """
        update_data = {
            "status": OutreachStatus.DELIVERED.value,
            "delivery.delivered_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        
        return await self.update(outreach_id, update_data)
    
    async def mark_read(
        self,
        outreach_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Mark outreach as read.
        
        Args:
            outreach_id: Outreach document ID
            
        Returns:
            Updated outreach
        """
        update_data = {
            "status": OutreachStatus.READ.value,
            "delivery.read_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        
        return await self.update(outreach_id, update_data)
    
    async def mark_responded(
        self,
        outreach_id: str,
        action: str,
        booking_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Mark outreach as responded.
        
        Args:
            outreach_id: Outreach document ID
            action: Customer action (booked, declined, etc.)
            booking_id: Booking ID if created
            
        Returns:
            Updated outreach
        """
        now = datetime.utcnow()
        
        update_data = {
            "status": OutreachStatus.RESPONDED.value,
            "response": {
                "received": True,
                "action": action,
                "responded_at": now.isoformat(),
                "booking_id": booking_id,
            },
            "updated_at": now.isoformat(),
        }
        
        return await self.update(outreach_id, update_data)
    
    async def mark_failed(
        self,
        outreach_id: str,
        error: str,
    ) -> Optional[Dict[str, Any]]:
        """Mark outreach as failed.
        
        Args:
            outreach_id: Outreach document ID
            error: Error message
            
        Returns:
            Updated outreach
        """
        update_data = {
            "status": OutreachStatus.FAILED.value,
            "delivery.error": error,
            "updated_at": datetime.utcnow().isoformat(),
        }
        
        return await self.update(outreach_id, update_data)
    
    async def mark_expired(
        self,
        outreach_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Mark outreach as expired.
        
        Args:
            outreach_id: Outreach document ID
            
        Returns:
            Updated outreach
        """
        update_data = {
            "status": OutreachStatus.EXPIRED.value,
            "updated_at": datetime.utcnow().isoformat(),
        }
        
        return await self.update(outreach_id, update_data)
    
    async def get_expired_outreach(
        self,
        salon_id: str,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get expired but not marked outreach.
        
        Args:
            salon_id: Salon ID
            limit: Maximum results
            
        Returns:
            List of expired outreach
        """
        now = datetime.utcnow()
        
        return await self.list(
            salon_id=salon_id,
            filters=[
                ("status", "in", [OutreachStatus.PENDING.value, OutreachStatus.SENT.value, OutreachStatus.DELIVERED.value]),
                ("expires_at", "<", now.isoformat()),
            ],
            limit=limit,
        )
    
    async def get_outreach_stats(
        self,
        salon_id: str,
        days: int = 7,
    ) -> Dict[str, Any]:
        """Get outreach statistics.
        
        Args:
            salon_id: Salon ID
            days: Number of days to analyze
            
        Returns:
            Statistics summary
        """
        start_date = date.today() - timedelta(days=days)
        
        outreach_list = await self.list(
            salon_id=salon_id,
            filters=[("created_at", ">=", start_date.isoformat())],
            limit=500,
        )
        
        stats = {
            "total": len(outreach_list),
            "by_status": {},
            "by_channel": {},
            "by_type": {},
            "conversion_rate": 0,
            "response_rate": 0,
            "avg_response_time_seconds": 0,
        }
        
        responded_count = 0
        converted_count = 0
        response_times = []
        
        for outreach in outreach_list:
            # By status
            status = outreach.get("status", "unknown")
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
            
            # By channel
            channel = outreach.get("channel", "unknown")
            stats["by_channel"][channel] = stats["by_channel"].get(channel, 0) + 1
            
            # By type
            otype = outreach.get("outreach_type", "unknown")
            stats["by_type"][otype] = stats["by_type"].get(otype, 0) + 1
            
            # Response tracking
            response = outreach.get("response", {})
            if response.get("received"):
                responded_count += 1
                
                if response.get("action") == "booked":
                    converted_count += 1
                
                # Calculate response time
                if response.get("responded_at") and outreach.get("delivery", {}).get("sent_at"):
                    sent = datetime.fromisoformat(outreach["delivery"]["sent_at"])
                    responded = datetime.fromisoformat(response["responded_at"])
                    response_times.append((responded - sent).total_seconds())
        
        if stats["total"] > 0:
            stats["response_rate"] = responded_count / stats["total"]
            stats["conversion_rate"] = converted_count / stats["total"]
        
        if response_times:
            stats["avg_response_time_seconds"] = sum(response_times) / len(response_times)
        
        return stats
    
    async def get_recent_by_phone(
        self,
        phone: str,
        salon_id: str,
        hours: int = 24,
    ) -> List[Dict[str, Any]]:
        """Get recent outreach to a phone number.
        
        Args:
            phone: Phone number
            salon_id: Salon ID
            hours: Hours to look back
            
        Returns:
            List of recent outreach
        """
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        return await self.list(
            salon_id=salon_id,
            filters=[
                ("customer_phone", "==", phone),
                ("created_at", ">=", cutoff.isoformat()),
            ],
            limit=10,
        )
