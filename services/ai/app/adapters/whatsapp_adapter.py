"""WhatsApp Adapter for Salon Flow AI Service

Integrates with the Notification Service to send WhatsApp messages.
Supports both platform-level and salon-specific (BYOA) credentials.
"""
import os
import httpx
from typing import Optional, Dict, Any
from dataclasses import dataclass
import structlog

logger = structlog.get_logger()


@dataclass
class WhatsAppMessage:
    """WhatsApp message data"""
    to: str
    message: str
    media_url: Optional[str] = None
    salon_id: Optional[str] = None


@dataclass
class WhatsAppResult:
    """Result of WhatsApp send operation"""
    success: bool
    message_sid: Optional[str] = None
    error: Optional[str] = None
    to: Optional[str] = None
    status: Optional[str] = None


class WhatsAppAdapter:
    """Adapter for sending WhatsApp messages via Notification Service"""
    
    def __init__(
        self,
        notification_service_url: str = None,
        timeout: float = 30.0
    ):
        self.notification_service_url = notification_service_url or os.getenv(
            "NOTIFICATION_SERVICE_URL",
            "http://notification-service:8002"
        )
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
    
    @property
    def client(self) -> httpx.AsyncClient:
        """Lazy initialization of HTTP client"""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client
    
    async def close(self):
        """Close HTTP client"""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    async def send_message(
        self,
        to: str,
        message: str,
        media_url: Optional[str] = None,
        salon_id: Optional[str] = None,
    ) -> WhatsAppResult:
        """Send WhatsApp message via Notification Service"""
        try:
            url = f"{self.notification_service_url}/api/v1/whatsapp/send"
            
            payload = {
                "to": to,
                "message": message,
                "media_url": media_url,
                "salon_id": salon_id
            }
            
            logger.info(
                "Sending WhatsApp via Notification Service",
                to=to,
                salon_id=salon_id
            )
            
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            
            return WhatsAppResult(
                success=data.get("success", False),
                message_sid=data.get("message_sid"),
                error=data.get("error"),
                to=data.get("to"),
                status=data.get("status")
            )
            
        except httpx.HTTPStatusError as e:
            logger.error(
                "HTTP error sending WhatsApp",
                status_code=e.response.status_code,
                error=str(e)
            )
            return WhatsAppResult(
                success=False,
                error=f"HTTP error: {e.response.status_code}",
                to=to
            )
        except httpx.RequestError as e:
            logger.error("Request error sending WhatsApp", error=str(e))
            return WhatsAppResult(
                success=False,
                error=f"Request error: {str(e)}",
                to=to
            )
        except Exception as e:
            logger.error("Error sending WhatsApp", error=str(e))
            return WhatsAppResult(
                success=False,
                error=str(e),
                to=to
            )
    
    async def send_booking_confirmation(
        self,
        to: str,
        customer_name: str,
        service: str,
        stylist: str,
        datetime: str,
        salon_name: str,
        salon_id: Optional[str] = None,
    ) -> WhatsAppResult:
        """Send booking confirmation message"""
        message = f"""🎉 Booking Confirmed!

Hello {customer_name},

Your appointment at {salon_name} is confirmed:

💇 Service: {service}
👤 Stylist: {stylist}
📅 Date & Time: {datetime}

Please arrive 5 minutes early. To reschedule, reply with 'RESCHEDULE'.

Thank you for choosing {salon_name}!"""
        
        return await self.send_message(to, message, salon_id=salon_id)
    
    async def send_booking_reminder(
        self,
        to: str,
        customer_name: str,
        service: str,
        stylist: str,
        datetime: str,
        salon_name: str,
        salon_id: Optional[str] = None,
    ) -> WhatsAppResult:
        """Send booking reminder (24h before)"""
        message = f"""⏰ Appointment Reminder

Hello {customer_name},

This is a reminder for your appointment tomorrow:

💇 Service: {service}
👤 Stylist: {stylist}
📅 Time: {datetime}

See you at {salon_name}!

To cancel, reply 'CANCEL'. To reschedule, reply 'RESCHEDULE'."""
        
        return await self.send_message(to, message, salon_id=salon_id)
    
    async def send_welcome_message(
        self,
        to: str,
        salon_name: str,
        salon_id: Optional[str] = None,
    ) -> WhatsAppResult:
        """Send welcome message to new customer"""
        message = f"""👋 Welcome to {salon_name}!

Thank you for choosing us. We're excited to serve you!

Here's what you can do:
• Book appointments
• View our services
• Check your loyalty points
• Get exclusive offers

Reply with 'BOOK' to schedule an appointment, or 'MENU' to see our services."""
        
        return await self.send_message(to, message, salon_id=salon_id)
    
    async def send_loyalty_update(
        self,
        to: str,
        customer_name: str,
        points_earned: int,
        total_points: int,
        salon_name: str,
        salon_id: Optional[str] = None,
    ) -> WhatsAppResult:
        """Send loyalty points update"""
        message = f"""🎁 Loyalty Points Earned!

Hello {customer_name},

You earned {points_earned} points from your recent visit!

💰 Total Points: {total_points}

Redeem points for discounts on your next visit.

Thank you for being a loyal customer at {salon_name}!"""
        
        return await self.send_message(to, message, salon_id=salon_id)
    
    async def send_feedback_request(
        self,
        to: str,
        customer_name: str,
        service: str,
        stylist: str,
        salon_name: str,
        salon_id: Optional[str] = None,
    ) -> WhatsAppResult:
        """Send feedback request after service"""
        message = f"""⭐ How was your experience?

Hello {customer_name},

We hope you loved your {service} with {stylist}!

Please rate your experience:

1️⃣ - Poor
2️⃣ - Fair
3️⃣ - Good
4️⃣ - Very Good
5️⃣ - Excellent

Reply with your rating (1-5) or leave a comment.

Thank you for choosing {salon_name}! 💇"""
        
        return await self.send_message(to, message, salon_id=salon_id)
    
    async def send_promotional_offer(
        self,
        to: str,
        customer_name: str,
        offer_title: str,
        offer_details: str,
        valid_until: str,
        salon_name: str,
        salon_id: Optional[str] = None,
    ) -> WhatsAppResult:
        """Send promotional offer"""
        message = f"""🎊 Special Offer Just for You!

Hello {customer_name},

{offer_title}

{offer_details}

⏰ Valid until: {valid_until}

Reply 'CLAIM' to book your appointment with this offer!

- {salon_name} Team"""
        
        return await self.send_message(to, message, salon_id=salon_id)
