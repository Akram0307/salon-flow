"""Event Publisher Utility for GCP Pub/Sub Integration

Provides async methods for publishing events to GCP Pub/Sub for AI service consumption.
This module wraps the synchronous EventPublisher with async methods for use in
async FastAPI endpoints.
"""
import asyncio
from typing import Dict, Any, Optional
from functools import partial
import structlog

from app.services.event_publisher import EventPublisher, EventTypes, get_publisher

logger = structlog.get_logger()


class AsyncEventPublisher:
    """Async wrapper for EventPublisher with convenience methods for domain events.
    
    This class provides async methods for publishing booking, customer, and inventory
    events to GCP Pub/Sub. The underlying EventPublisher is synchronous, so all
    publish operations are run in a thread pool executor.
    
    Attributes:
        _publisher: The underlying synchronous EventPublisher instance
    """
    
    def __init__(self):
        self._publisher: Optional[EventPublisher] = None
    
    @property
    def publisher(self) -> EventPublisher:
        """Lazy initialization of the underlying publisher."""
        if self._publisher is None:
            self._publisher = get_publisher()
        return self._publisher
    
    
    async def _publish_async(
        self,
        event_type: str,
        data: Dict[str, Any],
        salon_id: str,
        **kwargs
    ) -> str:
        """Run synchronous publish in a thread pool.
        
        Args:
            event_type: Type of event (e.g., 'booking.created')
            data: Event payload data
            salon_id: Salon ID for multi-tenant routing
            **kwargs: Additional arguments for publish
            
        Returns:
            Event ID if published successfully, empty string otherwise
        """
        loop = asyncio.get_event_loop()
        success = await loop.run_in_executor(
            None,
            partial(self.publisher.publish, event_type, data, salon_id, **kwargs)
        )
        return f"{event_type}-{salon_id}" if success else ""
    
    
    async def publish_booking_event(
        self,
        event_type: str,  # created, updated, cancelled, completed
        booking_data: Dict[str, Any],
        salon_id: str
    ) -> str:
        """Publish booking-related events.
        
        Args:
            event_type: One of 'created', 'updated', 'cancelled', 'completed', 'no_show'
            booking_data: Booking data dictionary
            salon_id: Salon ID
            
        Returns:
            Event ID if published successfully, empty string otherwise
            
        Example:
            await publisher.publish_booking_event(
                "created",
                {"booking_id": "123", "customer_id": "456", ...},
                "salon_789"
            )
        """
        # Map short event type to full event type
        event_type_map = {
            "created": EventTypes.BOOKING_CREATED,
            "updated": EventTypes.BOOKING_UPDATED,
            "cancelled": EventTypes.BOOKING_CANCELLED,
            "completed": EventTypes.BOOKING_COMPLETED,
            "no_show": EventTypes.BOOKING_NO_SHOW,
        }
        
        full_event_type = event_type_map.get(event_type, f"booking.{event_type}")
        
        logger.info(
            "publishing_booking_event",
            event_type=full_event_type,
            booking_id=booking_data.get("booking_id"),
            salon_id=salon_id
        )
        
        return await self._publish_async(full_event_type, booking_data, salon_id)
    
    
    async def publish_customer_event(
        self,
        event_type: str,  # created, updated, feedback
        customer_data: Dict[str, Any],
        salon_id: str
    ) -> str:
        """Publish customer-related events.
        
        Args:
            event_type: One of 'created', 'updated', 'visited', 'feedback'
            customer_data: Customer data dictionary
            salon_id: Salon ID
            
        Returns:
            Event ID if published successfully, empty string otherwise
            
        Example:
            await publisher.publish_customer_event(
                "created",
                {"customer_id": "123", "name": "John", ...},
                "salon_789"
            )
        """
        # Map short event type to full event type
        event_type_map = {
            "created": EventTypes.CUSTOMER_CREATED,
            "updated": EventTypes.CUSTOMER_UPDATED,
            "visited": EventTypes.CUSTOMER_VISITED,
            "feedback": EventTypes.CUSTOMER_FEEDBACK,
        }
        
        full_event_type = event_type_map.get(event_type, f"customer.{event_type}")
        
        logger.info(
            "publishing_customer_event",
            event_type=full_event_type,
            customer_id=customer_data.get("customer_id"),
            salon_id=salon_id
        )
        
        return await self._publish_async(full_event_type, customer_data, salon_id)
    
    
    async def publish_inventory_event(
        self,
        event_type: str,  # low_stock, reordered, updated
        inventory_data: Dict[str, Any],
        salon_id: str
    ) -> str:
        """Publish inventory-related events.
        
        Args:
            event_type: One of 'low_stock', 'reordered', 'updated'
            inventory_data: Inventory data dictionary
            salon_id: Salon ID
            
        Returns:
            Event ID if published successfully, empty string otherwise
            
        Example:
            await publisher.publish_inventory_event(
                "low_stock",
                {"product_id": "123", "quantity": 5, ...},
                "salon_789"
            )
        """
        # Map short event type to full event type
        event_type_map = {
            "low_stock": EventTypes.INVENTORY_LOW,
            "reordered": EventTypes.INVENTORY_UPDATED,
            "updated": EventTypes.INVENTORY_UPDATED,
        }
        
        full_event_type = event_type_map.get(event_type, f"inventory.{event_type}")
        
        logger.info(
            "publishing_inventory_event",
            event_type=full_event_type,
            product_id=inventory_data.get("product_id"),
            salon_id=salon_id
        )
        
        return await self._publish_async(full_event_type, inventory_data, salon_id)
    
    
    async def publish_staff_event(
        self,
        event_type: str,  # checked_in, checked_out, shift_updated
        staff_data: Dict[str, Any],
        salon_id: str
    ) -> str:
        """Publish staff-related events.
        
        Args:
            event_type: One of 'checked_in', 'checked_out', 'shift_updated'
            staff_data: Staff data dictionary
            salon_id: Salon ID
            
        Returns:
            Event ID if published successfully, empty string otherwise
        """
        event_type_map = {
            "checked_in": EventTypes.STAFF_CHECKED_IN,
            "checked_out": EventTypes.STAFF_CHECKED_OUT,
            "shift_updated": EventTypes.STAFF_SHIFT_UPDATED,
        }
        
        full_event_type = event_type_map.get(event_type, f"staff.{event_type}")
        
        
        logger.info(
            "publishing_staff_event",
            event_type=full_event_type,
            staff_id=staff_data.get("staff_id"),
            salon_id=salon_id
        )
        
        return await self._publish_async(full_event_type, staff_data, salon_id)
    
    
    async def publish_payment_event(
        self,
        event_type: str,  # received, refunded
        payment_data: Dict[str, Any],
        salon_id: str
    ) -> str:
        """Publish payment-related events.
        
        Args:
            event_type: One of 'received', 'refunded'
            payment_data: Payment data dictionary
            salon_id: Salon ID
            
        Returns:
            Event ID if published successfully, empty string otherwise
        """
        event_type_map = {
            "received": EventTypes.PAYMENT_RECEIVED,
            "refunded": EventTypes.PAYMENT_REFUNDED,
        }
        
        full_event_type = event_type_map.get(event_type, f"payment.{event_type}")
        
        
        logger.info(
            "publishing_payment_event",
            event_type=full_event_type,
            payment_id=payment_data.get("payment_id"),
            salon_id=salon_id
        )
        
        return await self._publish_async(full_event_type, payment_data, salon_id)
    
    
    async def publish_marketing_event(
        self,
        event_type: str,  # campaign_triggered, offer_redeemed
        marketing_data: Dict[str, Any],
        salon_id: str
    ) -> str:
        """Publish marketing-related events.
        
        Args:
            event_type: One of 'campaign_triggered', 'offer_redeemed'
            marketing_data: Marketing data dictionary
            salon_id: Salon ID
            
        Returns:
            Event ID if published successfully, empty string otherwise
        """
        event_type_map = {
            "campaign_triggered": EventTypes.CAMPAIGN_TRIGGERED,
            "offer_redeemed": EventTypes.OFFER_REDEEMED,
        }
        
        full_event_type = event_type_map.get(event_type, f"marketing.{event_type}")
        
        logger.info(
            "publishing_marketing_event",
            event_type=full_event_type,
            campaign_id=marketing_data.get("campaign_id"),
            salon_id=salon_id
        )
        
        return await self._publish_async(full_event_type, marketing_data, salon_id)


# Singleton instance for convenience
_async_publisher: Optional[AsyncEventPublisher] = None


def get_async_publisher() -> AsyncEventPublisher:
    """Get or create the async event publisher singleton."""
    global _async_publisher
    if _async_publisher is None:
        _async_publisher = AsyncEventPublisher()
    return _async_publisher


# Convenience async functions for direct import
async def publish_booking_event(
    event_type: str,
    booking_data: Dict[str, Any],
    salon_id: str
) -> str:
    """Convenience function to publish booking events."""
    return await get_async_publisher().publish_booking_event(event_type, booking_data, salon_id)


async def publish_customer_event(
    event_type: str,
    customer_data: Dict[str, Any],
    salon_id: str
) -> str:
    """Convenience function to publish customer events."""
    return await get_async_publisher().publish_customer_event(event_type, customer_data, salon_id)


async def publish_inventory_event(
    event_type: str,
    inventory_data: Dict[str, Any],
    salon_id: str
) -> str:
    """Convenience function to publish inventory events."""
    return await get_async_publisher().publish_inventory_event(event_type, inventory_data, salon_id)


__all__ = [
    "AsyncEventPublisher",
    "get_async_publisher",
    "publish_booking_event",
    "publish_customer_event",
    "publish_inventory_event",
]
