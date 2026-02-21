"""Event Publisher for GCP Pub/Sub

Publishes domain events to GCP Pub/Sub for event-driven architecture.
Events are consumed by AI service and other subscribers.
"""
import json
import structlog
from typing import Optional, Dict, Any
from datetime import datetime
from google.cloud import pubsub_v1
from google.api_core import exceptions as gcp_exceptions

from app.core.config import settings

logger = structlog.get_logger()
# settings imported directly


class EventPublisher:
    """GCP Pub/Sub event publisher with batching and error handling"""
    
    def __init__(self):
        self._publisher: Optional[pubsub_v1.PublisherClient] = None
        self._topic_path: Optional[str] = None
        
    @property
    def publisher(self) -> pubsub_v1.PublisherClient:
        """Lazy initialization of publisher client"""
        if self._publisher is None:
            self._publisher = pubsub_v1.PublisherClient()
            self._topic_path = self._publisher.topic_path(
                settings.gcp_project_id,
                settings.pubsub_topic
            )
        return self._publisher
    
    def publish(
        self,
        event_type: str,
        data: Dict[str, Any],
        salon_id: str,
        correlation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Publish an event to Pub/Sub
        
        Args:
            event_type: Type of event (e.g., 'booking.created', 'customer.updated')
            data: Event payload data
            salon_id: Salon ID for multi-tenant routing
            correlation_id: Optional correlation ID for tracing
            metadata: Optional additional metadata
            
        Returns:
            True if published successfully, False otherwise
        """
        event = {
            "event_type": event_type,
            "event_id": f"{event_type}-{datetime.utcnow().timestamp()}",
            "timestamp": datetime.utcnow().isoformat(),
            "salon_id": salon_id,
            "correlation_id": correlation_id,
            "data": data,
            "metadata": metadata or {}
        }
        
        try:
            message_data = json.dumps(event).encode("utf-8")
            future = self.publisher.publish(
                self._topic_path,
                message_data,
                event_type=event_type,
                salon_id=salon_id
            )
            # Don't wait for result in async context
            logger.info(
                "event_published",
                event_type=event_type,
                salon_id=salon_id,
                message_id=future.result(timeout=5)
            )
            return True
            
        except gcp_exceptions.GoogleAPICallError as e:
            logger.error("pubsub_publish_error", error=str(e), event_type=event_type)
            return False
        except Exception as e:
            logger.error("event_publish_failed", error=str(e), event_type=event_type)
            return False


# Singleton instance
_publisher: Optional[EventPublisher] = None


def get_publisher() -> EventPublisher:
    """Get or create the event publisher singleton"""
    global _publisher
    if _publisher is None:
        _publisher = EventPublisher()
    return _publisher


def publish_event(
    event_type: str,
    data: Dict[str, Any],
    salon_id: str,
    **kwargs
) -> bool:
    """Convenience function to publish events"""
    return get_publisher().publish(event_type, data, salon_id, **kwargs)


# Event type constants for type safety
class EventTypes:
    """Standard event types for the salon domain"""
    # Booking events
    BOOKING_CREATED = "booking.created"
    BOOKING_UPDATED = "booking.updated"
    BOOKING_CANCELLED = "booking.cancelled"
    BOOKING_COMPLETED = "booking.completed"
    BOOKING_NO_SHOW = "booking.no_show"
    
    # Customer events
    CUSTOMER_CREATED = "customer.created"
    CUSTOMER_UPDATED = "customer.updated"
    CUSTOMER_VISITED = "customer.visited"
    CUSTOMER_FEEDBACK = "customer.feedback"
    
    # Staff events
    STAFF_CHECKED_IN = "staff.checked_in"
    STAFF_CHECKED_OUT = "staff.checked_out"
    STAFF_SHIFT_UPDATED = "staff.shift_updated"
    
    # Inventory events
    INVENTORY_LOW = "inventory.low"
    INVENTORY_UPDATED = "inventory.updated"
    
    # Payment events
    PAYMENT_RECEIVED = "payment.received"
    PAYMENT_REFUNDED = "payment.refunded"
    
    # Marketing events
    CAMPAIGN_TRIGGERED = "campaign.triggered"
    OFFER_REDEEMED = "offer.redeemed"
