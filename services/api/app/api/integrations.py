"""Integrations Router for Salon Flow API.

Handles multi-tenant Twilio/WhatsApp configuration:
- Platform mode: Use platform-provided Twilio subaccount
- BYOK mode: Bring Your Own Keys (salon's own Twilio account)
"""
from datetime import datetime
from typing import Optional
import os

import structlog
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from google.cloud import firestore
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

from app.api.dependencies import get_current_user, AuthContext, require_owner
from app.core.firebase import get_firestore_async
from app.core.encryption import encrypt_credential, decrypt_credential
from app.schemas.integration import (
    IntegrationMode,
    IntegrationStatus,
    TwilioConfigRequest,
    TwilioConfigResponse,
    TwilioTestRequest,
    TwilioTestResponse,
    ProvisionNumberRequest,
    ProvisionNumberResponse,
    IntegrationStatusResponse,
    SalonIntegration,
)

logger = structlog.get_logger()
router = APIRouter()

# Collection name for salon integrations
INTEGRATIONS_COLLECTION = "salon_integrations"

# Platform Twilio credentials (from environment)
PLATFORM_TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
PLATFORM_TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
PLATFORM_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")


# ============================================================================
# Helper Functions
# ============================================================================

async def get_salon_integration(salon_id: str) -> Optional[SalonIntegration]:
    """Get salon integration from Firestore."""
    db = get_firestore_async()
    doc_ref = db.collection(INTEGRATIONS_COLLECTION).document(salon_id)
    doc = await doc_ref.get()
    
    if not doc.exists:
        return None
    
    return SalonIntegration.from_firestore(doc.to_dict())


async def save_salon_integration(integration: SalonIntegration) -> None:
    """Save salon integration to Firestore."""
    db = get_firestore_async()
    doc_ref = db.collection(INTEGRATIONS_COLLECTION).document(integration.salon_id)
    integration.updated_at = datetime.utcnow()
    await doc_ref.set(integration.to_firestore())


async def delete_salon_integration(salon_id: str) -> None:
    """Delete salon integration from Firestore."""
    db = get_firestore_async()
    doc_ref = db.collection(INTEGRATIONS_COLLECTION).document(salon_id)
    await doc_ref.delete()


async def test_twilio_credentials(
    account_sid: str,
    auth_token: str,
    whatsapp_number: str,
    test_to: str,
) -> tuple[bool, str, Optional[str]]:
    """Test Twilio credentials by sending a test message.
    
    Returns:
        Tuple of (success, message, message_sid)
    """
    try:
        client = Client(account_sid, auth_token)
        
        # Format numbers
        from_number = f"whatsapp:{whatsapp_number}" if not whatsapp_number.startswith("whatsapp:") else whatsapp_number
        to_number = f"whatsapp:{test_to}" if not test_to.startswith("whatsapp:") else test_to
        
        # Ensure E.164 format
        if not from_number.replace("whatsapp:", "").startswith("+"):
            from_number = f"whatsapp:+{from_number.replace('whatsapp:', '')}"
        if not to_number.replace("whatsapp:", "").startswith("+"):
            to_number = f"whatsapp:+{to_number.replace('whatsapp:', '')}"
        
        # Send test message
        msg = client.messages.create(
            from_=from_number,
            body="🎉 Salon Flow Test Message\n\nYour WhatsApp integration is working correctly!",
            to=to_number,
        )
        
        return True, "Test message sent successfully", msg.sid
        
    except TwilioRestException as e:
        logger.error("Twilio test failed", error=str(e), code=e.code)
        return False, f"Twilio error: {e.msg}", None
    except Exception as e:
        logger.error("Test failed", error=str(e))
        return False, str(e), None


# ============================================================================
# API Endpoints
# ============================================================================

@router.get("/twilio", response_model=TwilioConfigResponse)
async def get_twilio_config(auth: AuthContext = Depends(get_current_user)):
    """Get current Twilio configuration for the salon.
    
    Returns masked configuration (sensitive fields hidden).
    """
    try:
        integration = await get_salon_integration(auth.salon_id)
        
        if not integration:
            # No BYOK config, return platform mode
            return TwilioConfigResponse(
                salon_id=auth.salon_id,
                mode=IntegrationMode.PLATFORM,
                status=IntegrationStatus.ACTIVE,
                whatsapp_number=PLATFORM_WHATSAPP_NUMBER,
            )
        
        # Return masked config
        return TwilioConfigResponse(
            salon_id=integration.salon_id,
            mode=integration.mode,
            status=integration.status,
            whatsapp_number=integration.twilio_whatsapp_number,
            sms_number=integration.twilio_sms_number,
            account_sid_preview=integration.twilio_account_sid[:4] + "****" + integration.twilio_account_sid[-4:] if integration.twilio_account_sid else None,
            created_at=integration.created_at,
            updated_at=integration.updated_at,
        )
        
    except Exception as e:
        logger.error("Error getting Twilio config", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/twilio", response_model=TwilioConfigResponse)
async def save_twilio_config(
    request: TwilioConfigRequest,
    background_tasks: BackgroundTasks,
    auth: AuthContext = Depends(get_current_user),
):
    """Save Twilio BYOK configuration.
    
    Encrypts and stores the salon's own Twilio credentials.
    """
    try:
        # Encrypt sensitive credentials
        encrypted_sid = encrypt_credential(request.account_sid)
        encrypted_token = encrypt_credential(request.auth_token)
        
        # Create or update integration
        integration = await get_salon_integration(auth.salon_id)
        
        if integration:
            integration.twilio_account_sid = encrypted_sid
            integration.twilio_auth_token = encrypted_token
            integration.twilio_whatsapp_number = request.whatsapp_number
            integration.twilio_sms_number = request.sms_number
            integration.mode = IntegrationMode.BYOK
            integration.status = IntegrationStatus.PENDING
            integration.updated_at = datetime.utcnow()
        else:
            integration = SalonIntegration(
                salon_id=auth.salon_id,
                twilio_account_sid=encrypted_sid,
                twilio_auth_token=encrypted_token,
                twilio_whatsapp_number=request.whatsapp_number,
                twilio_sms_number=request.sms_number,
                mode=IntegrationMode.BYOK,
                status=IntegrationStatus.PENDING,
            )
        
        await save_salon_integration(integration)
        
        logger.info(
            "Twilio BYOK config saved",
            salon_id=auth.salon_id,
            mode="byok",
        )
        
        return TwilioConfigResponse(
            salon_id=integration.salon_id,
            mode=integration.mode,
            status=integration.status,
            whatsapp_number=integration.twilio_whatsapp_number,
            sms_number=integration.twilio_sms_number,
            account_sid_preview=request.account_sid[:4] + "****" + request.account_sid[-4:],
            created_at=integration.created_at,
            updated_at=integration.updated_at,
        )
        
    except Exception as e:
        logger.error("Error saving Twilio config", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/twilio")
async def delete_twilio_config(
    auth: AuthContext = Depends(get_current_user),
):
    """Delete BYOK configuration and switch to platform mode."""
    try:
        await delete_salon_integration(auth.salon_id)
        
        logger.info(
            "Twilio BYOK config deleted, switching to platform",
            salon_id=auth.salon_id,
        )
        
        return {
            "success": True,
            "message": "BYOK configuration removed. Now using platform Twilio.",
            "mode": "platform",
        }
        
    except Exception as e:
        logger.error("Error deleting Twilio config", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/twilio/test", response_model=TwilioTestResponse)
async def test_twilio_config(
    request: TwilioTestRequest,
    auth: AuthContext = Depends(get_current_user),
):
    """Test Twilio configuration by sending a test message.
    
    Uses BYOK credentials if configured, otherwise platform credentials.
    """
    try:
        integration = await get_salon_integration(auth.salon_id)
        
        # Determine which credentials to use
        if integration and integration.mode == IntegrationMode.BYOK:
            # Use BYOK credentials
            account_sid = decrypt_credential(integration.twilio_account_sid)
            auth_token = decrypt_credential(integration.twilio_auth_token)
            whatsapp_number = integration.twilio_whatsapp_number
            
            logger.info("Testing BYOK Twilio config", salon_id=auth.salon_id)
        else:
            # Use platform credentials
            account_sid = PLATFORM_TWILIO_ACCOUNT_SID
            auth_token = PLATFORM_TWILIO_AUTH_TOKEN
            whatsapp_number = PLATFORM_WHATSAPP_NUMBER
            
            if not account_sid or not auth_token:
                return TwilioTestResponse(
                    success=False,
                    message="Platform Twilio not configured",
                    error="Contact support to enable platform messaging",
                )
            
            logger.info("Testing platform Twilio config", salon_id=auth.salon_id)
        
        # Send test message
        success, message, sid = await test_twilio_credentials(
            account_sid=account_sid,
            auth_token=auth_token,
            whatsapp_number=whatsapp_number,
            test_to=request.to_number,
        )
        
        # Update integration status if BYOK
        if integration and integration.mode == IntegrationMode.BYOK:
            integration.status = IntegrationStatus.ACTIVE if success else IntegrationStatus.FAILED
            integration.last_verified_at = datetime.utcnow() if success else None
            integration.verification_error = None if success else message
            await save_salon_integration(integration)
        
        return TwilioTestResponse(
            success=success,
            message=message,
            message_sid=sid,
            error=None if success else message,
        )
        
    except Exception as e:
        logger.error("Error testing Twilio", error=str(e))
        return TwilioTestResponse(
            success=False,
            message="Test failed",
            error=str(e),
        )


@router.post("/twilio/provision", response_model=ProvisionNumberResponse)
async def provision_platform_number(
    request: ProvisionNumberRequest,
    auth: AuthContext = Depends(get_current_user),
):
    """Provision a platform Twilio number for the salon.
    
    This creates a subaccount under the platform's Twilio account
    and provisions a number with WhatsApp capability.
    """
    try:
        if not PLATFORM_TWILIO_ACCOUNT_SID or not PLATFORM_TWILIO_AUTH_TOKEN:
            return ProvisionNumberResponse(
                success=False,
                message="Platform Twilio not configured",
                error="Contact support to enable platform messaging",
            )
        
        client = Client(PLATFORM_TWILIO_ACCOUNT_SID, PLATFORM_TWILIO_AUTH_TOKEN)
        
        # Create subaccount for salon
        subaccount = client.api.accounts.create(
            friendly_name=f"Salon_{auth.salon_id[:12]}"
        )
        
        logger.info(
            "Created Twilio subaccount",
            salon_id=auth.salon_id,
            subaccount_sid=subaccount.sid,
        )
        
        # Search for available numbers
        search_params = {
            "capabilities": request.capabilities,
        }
        if request.area_code:
            search_params["area_code"] = request.area_code
        
        # Use subaccount client to provision number
        sub_client = Client(subaccount.sid, subaccount.auth_token)
        
        available_numbers = sub_client.available_phone_numbers.local.list(
            **search_params,
            limit=1,
        )
        
        if not available_numbers:
            return ProvisionNumberResponse(
                success=False,
                message="No available numbers found",
                error="Try a different area code or contact support",
            )
        
        # Purchase the number
        number = sub_client.incoming_phone_numbers.create(
            phone_number=available_numbers[0].phone_number,
            friendly_name=f"Salon_{auth.salon_id[:12]}_WhatsApp",
        )
        
        # Save integration with platform mode
        integration = SalonIntegration(
            salon_id=auth.salon_id,
            twilio_account_sid=encrypt_credential(subaccount.sid),
            twilio_auth_token=encrypt_credential(subaccount.auth_token),
            twilio_whatsapp_number=number.phone_number,
            mode=IntegrationMode.PLATFORM,
            status=IntegrationStatus.ACTIVE,
        )
        await save_salon_integration(integration)
        
        logger.info(
            "Provisioned platform Twilio number",
            salon_id=auth.salon_id,
            number=number.phone_number,
        )
        
        return ProvisionNumberResponse(
            success=True,
            message=f"Successfully provisioned {number.phone_number}",
            phone_number=number.phone_number,
        )
        
    except TwilioRestException as e:
        logger.error("Twilio provisioning failed", error=str(e))
        return ProvisionNumberResponse(
            success=False,
            message="Provisioning failed",
            error=f"Twilio error: {e.msg}",
        )
    except Exception as e:
        logger.error("Error provisioning number", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=IntegrationStatusResponse)
async def get_integration_status(
    auth: AuthContext = Depends(get_current_user),
):
    """Get overall integration status for the salon."""
    try:
        integration = await get_salon_integration(auth.salon_id)
        
        twilio_config = None
        if integration:
            twilio_config = TwilioConfigResponse(
                salon_id=integration.salon_id,
                mode=integration.mode,
                status=integration.status,
                whatsapp_number=integration.twilio_whatsapp_number,
                sms_number=integration.twilio_sms_number,
                account_sid_preview=integration.twilio_account_sid[:4] + "****" + integration.twilio_account_sid[-4:] if integration.twilio_account_sid else None,
                created_at=integration.created_at,
                updated_at=integration.updated_at,
            )
        
        return IntegrationStatusResponse(
            twilio=twilio_config,
            has_platform_access=bool(PLATFORM_TWILIO_ACCOUNT_SID),
            platform_whatsapp_number=PLATFORM_WHATSAPP_NUMBER,
        )
        
    except Exception as e:
        logger.error("Error getting integration status", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
