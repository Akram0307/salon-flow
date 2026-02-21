"""Twilio Client for WhatsApp and SMS messaging"""
import os
from typing import Optional, Dict, Any
from dataclasses import dataclass
import structlog
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

logger = structlog.get_logger()


@dataclass
class MessageResult:
    """Result of a message send operation"""
    success: bool
    message_sid: Optional[str] = None
    error: Optional[str] = None
    to: Optional[str] = None
    from_number: Optional[str] = None
    status: Optional[str] = None


class TwilioClient:
    """Twilio client for WhatsApp and SMS messaging"""
    
    def __init__(
        self,
        account_sid: str,
        auth_token: str,
        whatsapp_number: Optional[str] = None,
        sms_number: Optional[str] = None,
    ):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.whatsapp_number = whatsapp_number
        self.sms_number = sms_number
        self._client: Optional[Client] = None
    
    @property
    def client(self) -> Client:
        """Lazy initialization of Twilio client"""
        if self._client is None:
            self._client = Client(self.account_sid, self.auth_token)
        return self._client
    
    def _format_whatsapp_number(self, phone: str) -> str:
        """Format phone number for WhatsApp (whatsapp:+91XXXXXXXXXX)"""
        # Remove any existing whatsapp: prefix
        phone = phone.replace("whatsapp:", "")
        # Ensure E.164 format
        if not phone.startswith("+"):
            phone = f"+{phone}"
        return f"whatsapp:{phone}"
    
    def _format_sms_number(self, phone: str) -> str:
        """Format phone number for SMS (+91XXXXXXXXXX)"""
        phone = phone.replace("whatsapp:", "")
        if not phone.startswith("+"):
            phone = f"+{phone}"
        return phone
    
    async def send_whatsapp(
        self,
        to: str,
        message: str,
        media_url: Optional[str] = None,
    ) -> MessageResult:
        """Send WhatsApp message"""
        try:
            if not self.whatsapp_number:
                return MessageResult(
                    success=False,
                    error="WhatsApp number not configured"
                )
            
            from_number = self._format_whatsapp_number(self.whatsapp_number)
            to_number = self._format_whatsapp_number(to)
            
            logger.info(
                "Sending WhatsApp message",
                to=to_number,
                from_number=from_number
            )
            
            # Send message
            msg = self.client.messages.create(
                from_=from_number,
                body=message,
                to=to_number,
                media_url=media_url,
            )
            
            logger.info(
                "WhatsApp message sent",
                sid=msg.sid,
                status=msg.status
            )
            
            return MessageResult(
                success=True,
                message_sid=msg.sid,
                to=to,
                from_number=self.whatsapp_number,
                status=msg.status
            )
            
        except TwilioRestException as e:
            logger.error(
                "Twilio error sending WhatsApp",
                error=str(e),
                code=e.code
            )
            return MessageResult(
                success=False,
                error=f"Twilio error: {e.msg}",
                to=to
            )
        except Exception as e:
            logger.error("Error sending WhatsApp", error=str(e))
            return MessageResult(
                success=False,
                error=str(e),
                to=to
            )
    
    async def send_sms(
        self,
        to: str,
        message: str,
    ) -> MessageResult:
        """Send SMS message"""
        try:
            if not self.sms_number:
                return MessageResult(
                    success=False,
                    error="SMS number not configured"
                )
            
            from_number = self._format_sms_number(self.sms_number)
            to_number = self._format_sms_number(to)
            
            logger.info(
                "Sending SMS",
                to=to_number,
                from_number=from_number
            )
            
            msg = self.client.messages.create(
                from_=from_number,
                body=message,
                to=to_number,
            )
            
            logger.info(
                "SMS sent",
                sid=msg.sid,
                status=msg.status
            )
            
            return MessageResult(
                success=True,
                message_sid=msg.sid,
                to=to,
                from_number=self.sms_number,
                status=msg.status
            )
            
        except TwilioRestException as e:
            logger.error(
                "Twilio error sending SMS",
                error=str(e),
                code=e.code
            )
            return MessageResult(
                success=False,
                error=f"Twilio error: {e.msg}",
                to=to
            )
        except Exception as e:
            logger.error("Error sending SMS", error=str(e))
            return MessageResult(
                success=False,
                error=str(e),
                to=to
            )
    
    async def send_template_whatsapp(
        self,
        to: str,
        template_name: str,
        language: str = "en",
        components: Optional[list] = None,
    ) -> MessageResult:
        """Send WhatsApp template message (for approved templates)"""
        try:
            if not self.whatsapp_number:
                return MessageResult(
                    success=False,
                    error="WhatsApp number not configured"
                )
            
            from_number = self._format_whatsapp_number(self.whatsapp_number)
            to_number = self._format_whatsapp_number(to)
            
            # Build template content
            content = {
                "messaging_product": "whatsapp",
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {"code": language},
                }
            }
            
            if components:
                content["template"]["components"] = components
            
            
            # Use the API directly for template messages
            msg = self.client.messages.create(
                from_=from_number,
                content_sid=template_name,  # For content templates
                to=to_number,
            )
            
            return MessageResult(
                success=True,
                message_sid=msg.sid,
                to=to,
                from_number=self.whatsapp_number,
                status=msg.status
            )
            
        except Exception as e:
            logger.error("Error sending template", error=str(e))
            return MessageResult(
                success=False,
                error=str(e),
                to=to
            )
    
    def validate_webhook(self, url: str) -> bool:
        """Validate webhook URL is accessible"""
        # This would typically verify the webhook is properly configured
        return url.startswith("https://")


class TwilioClientFactory:
    """Factory for creating Twilio clients"""
    
    @staticmethod
    def from_settings(settings) -> TwilioClient:
        """Create Twilio client from settings"""
        return TwilioClient(
            account_sid=settings.twilio_account_sid,
            auth_token=settings.twilio_auth_token,
            whatsapp_number=settings.twilio_whatsapp_number,
        )
    
    @staticmethod
    def from_salon_config(
        account_sid: str,
        auth_token: str,
        whatsapp_number: str,
    ) -> TwilioClient:
        """Create Twilio client from salon-specific config (BYOA)"""
        return TwilioClient(
            account_sid=account_sid,
            auth_token=auth_token,
            whatsapp_number=whatsapp_number,
        )
