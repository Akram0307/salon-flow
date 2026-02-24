"""Notification Service Router with Multi-Tenant Support and Authentication"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List
import os
import structlog

from .config import settings
from .twilio_client import TwilioClient, TwilioClientFactory, MessageResult
from .core.auth import get_current_user, AuthContext

logger = structlog.get_logger()
router = APIRouter()


# ============================================================================
# Request/Response Models
# ============================================================================

class WhatsAppSendRequest(BaseModel):
    """Request to send WhatsApp message"""
    to: str = Field(..., description="Phone number in E.164 format (+91XXXXXXXXXX)")
    message: str = Field(..., description="Message content")
    media_url: Optional[str] = Field(None, description="Optional media URL")
    salon_id: Optional[str] = Field(None, description="Salon ID for BYOK")


class WhatsAppSendResponse(BaseModel):
    """Response from WhatsApp send"""
    success: bool
    message_sid: Optional[str] = None
    error: Optional[str] = None
    to: str
    status: Optional[str] = None


class SMSSendRequest(BaseModel):
    """Request to send SMS"""
    to: str = Field(..., description="Phone number in E.164 format")
    message: str = Field(..., description="Message content")
    salon_id: Optional[str] = Field(None, description="Salon ID for BYOK")


class SMSSendResponse(BaseModel):
    """Response from SMS send"""
    success: bool
    message_sid: Optional[str] = None
    error: Optional[str] = None
    to: str
    status: Optional[str] = None


class TestMessageRequest(BaseModel):
    """Request to send test message"""
    to: str = Field(..., description="Phone number to send test to")
    salon_id: Optional[str] = Field(None, description="Salon ID for BYOK")


class TestMessageResponse(BaseModel):
    """Response from test message"""
    success: bool
    message: str
    error: Optional[str] = None


class SalonIntegrationConfig(BaseModel):
    """Salon integration configuration from Firestore"""
    salon_id: str
    twilio_account_sid: Optional[str] = None  # Encrypted
    twilio_auth_token: Optional[str] = None   # Encrypted
    twilio_whatsapp_number: Optional[str] = None
    twilio_sms_number: Optional[str] = None
    mode: str = "platform"  # 'platform' or 'byok'
    status: str = "active"  # 'active', 'pending', 'failed'


# ============================================================================
# Multi-Tenant Credential Resolution
# ============================================================================

class CredentialResolver:
    """Resolves Twilio credentials for multi-tenant support.
    
    Resolution order:
    1. Check for salon-specific BYOK credentials in Firestore
    2. Fall back to platform credentials from GCP Secret Manager
    """
    
    def __init__(self):
        self._firestore_db = None
    
    @property
    def firestore_db(self):
        """Lazy initialization of Firestore client."""
        if self._firestore_db is None:
            from google.cloud import firestore
            self._firestore_db = firestore.AsyncClient(project=settings.gcp_project_id)
        return self._firestore_db
    
    async def get_salon_integration(self, salon_id: str) -> Optional[SalonIntegrationConfig]:
        """Get salon integration config from Firestore.
        
        Args:
            salon_id: The salon's unique identifier
            
        Returns:
            SalonIntegrationConfig if found, None otherwise
        """
        try:
            doc_ref = self.firestore_db.collection("salon_integrations").document(salon_id)
            doc = await doc_ref.get()
            
            if not doc.exists:
                return None
            
            data = doc.to_dict()
            return SalonIntegrationConfig(
                salon_id=salon_id,
                twilio_account_sid=data.get("twilio_account_sid"),
                twilio_auth_token=data.get("twilio_auth_token"),
                twilio_whatsapp_number=data.get("twilio_whatsapp_number"),
                twilio_sms_number=data.get("twilio_sms_number"),
                mode=data.get("mode", "platform"),
                status=data.get("status", "active"),
            )
            
        except Exception as e:
            logger.error("Error fetching salon integration", salon_id=salon_id, error=str(e))
            return None
    
    def _decrypt_credential(self, encrypted: str) -> str:
        """Decrypt a credential using the encryption service.
        
        Args:
            encrypted: Base64-encoded encrypted credential
            
        Returns:
            Decrypted plaintext credential
        """
        if not encrypted:
            return ""
        
        # Import encryption utility from API service location
        # For notification service, we'll use a simplified approach
        # In production, this should use the same encryption module
        try:
            from app.core.encryption import decrypt_credential
            return decrypt_credential(encrypted)
        except ImportError:
            # Fallback for standalone notification service
            import base64
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            from google.cloud import kms
            
            # This is a simplified version - in production, use the shared encryption module
            logger.warning("Using fallback decryption - should use shared encryption module")
            return encrypted  # Return as-is for now, proper implementation needed
    
    async def resolve_twilio_client(self, salon_id: Optional[str] = None) -> TwilioClient:
        """Resolve the appropriate Twilio client for a salon.
        
        Args:
            salon_id: Optional salon ID. If provided, checks for BYOK first.
            
        Returns:
            TwilioClient configured with appropriate credentials
            
        Raises:
            HTTPException: If no credentials are available
        """
        # If salon_id provided, check for BYOK credentials
        if salon_id:
            integration = await self.get_salon_integration(salon_id)
            
            if integration and integration.mode == "byok" and integration.status == "active":
                # Use salon's own Twilio credentials
                try:
                    account_sid = self._decrypt_credential(integration.twilio_account_sid)
                    auth_token = self._decrypt_credential(integration.twilio_auth_token)
                    
                    if account_sid and auth_token:
                        logger.info(
                            "Using BYOK Twilio credentials",
                            salon_id=salon_id,
                            mode="byok"
                        )
                        return TwilioClient(
                            account_sid=account_sid,
                            auth_token=auth_token,
                            whatsapp_number=integration.twilio_whatsapp_number,
                            sms_number=integration.twilio_sms_number,
                        )
                except Exception as e:
                    logger.warning(
                        "Failed to decrypt BYOK credentials, falling back to platform",
                        salon_id=salon_id,
                        error=str(e)
                    )
        
        # Fall back to platform credentials
        if not settings.twilio_account_sid or not settings.twilio_auth_token:
            raise HTTPException(
                status_code=503,
                detail="Twilio credentials not configured"
            )
        
        logger.info(
            "Using platform Twilio credentials",
            salon_id=salon_id or "default",
            mode="platform"
        )
        
        return TwilioClientFactory.from_settings(settings)


# Singleton credential resolver
_credential_resolver: Optional[CredentialResolver] = None


def get_credential_resolver() -> CredentialResolver:
    """Get the singleton credential resolver."""
    global _credential_resolver
    if _credential_resolver is None:
        _credential_resolver = CredentialResolver()
    return _credential_resolver


# ============================================================================
# API Endpoints (with Authentication)
# ============================================================================

@router.post("/whatsapp/send", response_model=WhatsAppSendResponse)
async def send_whatsapp(
    request: WhatsAppSendRequest,
    background_tasks: BackgroundTasks,
    current_user: AuthContext = Depends(get_current_user),
):
    """Send WhatsApp message to a phone number.
    
    Requires JWT authentication. Uses salon-specific BYOK credentials if configured,
    otherwise platform credentials.
    
    **Authentication Required**: Bearer token in Authorization header.
    """
    try:
        # Use authenticated user's salon_id if not provided in request
        effective_salon_id = request.salon_id or current_user.salon_id
        
        resolver = get_credential_resolver()
        client = await resolver.resolve_twilio_client(effective_salon_id)
        
        result = await client.send_whatsapp(
            to=request.to,
            message=request.message,
            media_url=request.media_url
        )
        
        logger.info(
            "WhatsApp message sent",
            to=request.to,
            salon_id=effective_salon_id,
            user_id=current_user.uid,
            success=result.success
        )
        
        return WhatsAppSendResponse(
            success=result.success,
            message_sid=result.message_sid,
            error=result.error,
            to=result.to or request.to,
            status=result.status
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error in WhatsApp send endpoint", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sms/send", response_model=SMSSendResponse)
async def send_sms(
    request: SMSSendRequest,
    current_user: AuthContext = Depends(get_current_user),
):
    """Send SMS message to a phone number.
    
    Requires JWT authentication. Uses salon-specific BYOK credentials if configured,
    otherwise platform credentials.
    
    **Authentication Required**: Bearer token in Authorization header.
    """
    try:
        # Use authenticated user's salon_id if not provided in request
        effective_salon_id = request.salon_id or current_user.salon_id
        
        resolver = get_credential_resolver()
        client = await resolver.resolve_twilio_client(effective_salon_id)
        
        result = await client.send_sms(
            to=request.to,
            message=request.message
        )
        
        logger.info(
            "SMS sent",
            to=request.to,
            salon_id=effective_salon_id,
            user_id=current_user.uid,
            success=result.success
        )
        
        return SMSSendResponse(
            success=result.success,
            message_sid=result.message_sid,
            error=result.error,
            to=result.to or request.to,
            status=result.status
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error in SMS send endpoint", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test", response_model=TestMessageResponse)
async def send_test_message(
    request: TestMessageRequest,
    current_user: AuthContext = Depends(get_current_user),
):
    """Send test WhatsApp message to verify configuration.
    
    Requires JWT authentication. Uses salon-specific BYOK credentials if configured,
    otherwise platform credentials.
    
    **Authentication Required**: Bearer token in Authorization header.
    """
    try:
        # Use authenticated user's salon_id if not provided in request
        effective_salon_id = request.salon_id or current_user.salon_id
        
        resolver = get_credential_resolver()
        client = await resolver.resolve_twilio_client(effective_salon_id)
        
        result = await client.send_whatsapp(
            to=request.to,
            message="🎉 Salon Flow Test Message\n\nYour WhatsApp integration is working correctly!"
        )
        
        if result.success:
            return TestMessageResponse(
                success=True,
                message=f"Test message sent successfully to {request.to}"
            )
        else:
            return TestMessageResponse(
                success=False,
                message="Failed to send test message",
                error=result.error
            )
    except HTTPException as e:
        return TestMessageResponse(
            success=False,
            message="Twilio not configured",
            error=str(e.detail)
        )
    except Exception as e:
        return TestMessageResponse(
            success=False,
            message="Error sending test",
            error=str(e)
        )


@router.get("/status")
async def get_notification_status():
    """Get notification service status."""
    return {
        "status": "operational",
        "whatsapp_configured": bool(settings.twilio_whatsapp_number),
        "sms_configured": bool(settings.twilio_account_sid),
        "platform_mode": settings.use_platform_twilio,
        "multi_tenant_enabled": True,
    }


@router.get("/salon/{salon_id}/config")
async def get_salon_notification_config(
    salon_id: str,
    current_user: AuthContext = Depends(get_current_user),
):
    """Get notification configuration for a specific salon.
    
    Requires JWT authentication. Returns the integration mode and status
    without exposing sensitive credentials.
    
    **Authentication Required**: Bearer token in Authorization header.
    """
    try:
        # Verify user has access to this salon
        if current_user.salon_id and current_user.salon_id != salon_id:
            raise HTTPException(
                status_code=403,
                detail="Access denied to this salon's configuration"
            )
        
        resolver = get_credential_resolver()
        integration = await resolver.get_salon_integration(salon_id)
        
        if not integration:
            return {
                "salon_id": salon_id,
                "mode": "platform",
                "status": "active",
                "whatsapp_number": settings.twilio_whatsapp_number,
                "using_platform": True,
            }
        
        
        return {
            "salon_id": salon_id,
            "mode": integration.mode,
            "status": integration.status,
            "whatsapp_number": integration.twilio_whatsapp_number,
            "using_platform": integration.mode == "platform",
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting salon notification config", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
