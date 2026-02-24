"""Webhook Endpoints for External Services.

Handles callbacks from:
- Twilio (WhatsApp/SMS delivery status, incoming messages)
- Payment gateways
- Other third-party integrations
"""
import json
from datetime import datetime
from typing import Optional
import structlog

from fastapi import APIRouter, Request, HTTPException, status, Depends, BackgroundTasks
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field

from app.core.config import settings
from app.models.autonomous import (
    OutreachModel,
    OutreachStatus,
    AuditLogModel,
    AuditEventType,
    AuditSeverity,
)
from app.services.autonomous.outreach_service import OutreachService

logger = structlog.get_logger()
router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


class TwilioStatusCallback(BaseModel):
    """Twilio message status callback."""
    message_sid: str = Field(..., alias="MessageSid")
    message_status: str = Field(..., alias="MessageStatus")
    from_number: str = Field(..., alias="From")
    to_number: str = Field(..., alias="To")
    account_sid: str = Field(..., alias="AccountSid")
    error_code: Optional[str] = Field(None, alias="ErrorCode")
    error_message: Optional[str] = Field(None, alias="ErrorMessage")
    
    class Config:
        populate_by_name = True


class TwilioIncomingMessage(BaseModel):
    """Twilio incoming message webhook."""
    message_sid: str = Field(..., alias="MessageSid")
    from_number: str = Field(..., alias="From")
    to_number: str = Field(..., alias="To")
    body: Optional[str] = Field(None, alias="Body")
    num_media: int = Field(0, alias="NumMedia")
    profile_name: Optional[str] = Field(None, alias="ProfileName")
    wa_id: Optional[str] = Field(None, alias="WaId")
    
    class Config:
        populate_by_name = True


@router.post("/twilio/status")
async def twilio_status_callback(
    request: Request,
    background_tasks: BackgroundTasks,
):
    """Handle Twilio message status callbacks.
    
    Receives delivery status updates for WhatsApp/SMS messages.
    Updates outreach records accordingly.
    """
    form_data = await request.form()
    
    message_sid = form_data.get("MessageSid", "")
    message_status = form_data.get("MessageStatus", "")
    to_number = form_data.get("To", "")
    error_code = form_data.get("ErrorCode")
    error_message = form_data.get("ErrorMessage")
    
    logger.info(
        "twilio_status_callback",
        message_sid=message_sid,
        status=message_status,
        to=to_number,
    )
    
    # Find outreach by message ID
    outreach_model = OutreachModel()
    outreach = await outreach_model.get_by_message_id(message_sid)
    
    if not outreach:
        logger.warning(
            "outreach_not_found_for_message",
            message_sid=message_sid,
        )
        return PlainTextResponse("OK", status_code=200)
    
    # Map Twilio status to our status
    status_map = {
        "queued": OutreachStatus.PENDING,
        "sent": OutreachStatus.SENT,
        "delivered": OutreachStatus.DELIVERED,
        "read": OutreachStatus.READ,
        "failed": OutreachStatus.FAILED,
        "undelivered": OutreachStatus.FAILED,
    }
    
    new_status = status_map.get(message_status.lower())
    if not new_status:
        logger.warning(
            "unknown_twilio_status",
            status=message_status,
        )
        return PlainTextResponse("OK", status_code=200)
    
    # Update outreach status
    outreach_service = OutreachService()
    
    try:
        await outreach_service.process_delivery_status(
            outreach_id=outreach["id"],
            status=new_status,
            message_id=message_sid,
            error=error_message or error_code,
        )
    except Exception as e:
        logger.error(
            "failed_to_update_outreach_status",
            outreach_id=outreach["id"],
            error=str(e),
        )
    
    return PlainTextResponse("OK", status_code=200)


@router.post("/twilio/incoming")
async def twilio_incoming_message(
    request: Request,
    background_tasks: BackgroundTasks,
):
    """Handle incoming WhatsApp/SMS messages.
    
    Processes customer responses to autonomous outreach.
    """
    form_data = await request.form()
    
    message_sid = form_data.get("MessageSid", "")
    from_number = form_data.get("From", "")
    body = form_data.get("Body", "").strip().lower()
    profile_name = form_data.get("ProfileName", "")
    wa_id = form_data.get("WaId", "")
    
    logger.info(
        "twilio_incoming_message",
        message_sid=message_sid,
        from_number=from_number,
        body=body[:50],  # Truncate for logging
    )
    
    # Find recent pending outreach to this number
    outreach_model = OutreachModel()
    
    # Extract phone number from whatsapp: prefix
    phone = from_number.replace("whatsapp:", "")
    
    recent_outreach = await outreach_model.get_recent_by_phone(
        phone=phone,
        salon_id=None,  # Search across salons
        hours=24,
    )
    
    if not recent_outreach:
        logger.info(
            "no_recent_outreach_for_incoming",
            from_number=from_number,
        )
        # Could forward to general WhatsApp concierge
        return PlainTextResponse("OK", status_code=200)
    
    # Parse response action
    action = _parse_response_action(body)
    
    if action:
        outreach_service = OutreachService()
        
        try:
            await outreach_service.process_customer_response(
                outreach_id=recent_outreach["id"],
                action=action,
            )
            
            logger.info(
                "outreach_response_processed",
                outreach_id=recent_outreach["id"],
                action=action,
            )
        except Exception as e:
            logger.error(
                "failed_to_process_response",
                outreach_id=recent_outreach["id"],
                error=str(e),
            )
    
    return PlainTextResponse("OK", status_code=200)


def _parse_response_action(body: str) -> Optional[str]:
    """Parse customer response to determine action.
    
    Supports:
    - 'yes', 'y', 'confirm', 'book' -> 'accept'
    - 'no', 'n', 'cancel', 'decline' -> 'decline'
    - '1', '2', '3' -> option selection
    """
    body = body.strip().lower()
    
    # Accept patterns
    accept_patterns = ["yes", "y", "confirm", "book", "sure", "ok", "okay", "haan", "ha", "ji"]
    if any(p in body for p in accept_patterns):
        return "accept"
    
    # Decline patterns
    decline_patterns = ["no", "n", "cancel", "decline", "nahi", "na", "nope"]
    if any(p in body for p in decline_patterns):
        return "decline"
    
    # Number selection (for multi-option messages)
    if body in ["1", "2", "3", "4", "5"]:
        return f"select_{body}"
    
    return None


@router.post("/twilio/voice")
async def twilio_voice_callback(request: Request):
    """Handle Twilio voice call callbacks.
    
    For voice receptionist agent integration.
    """
    form_data = await request.form()
    
    call_sid = form_data.get("CallSid", "")
    call_status = form_data.get("CallStatus", "")
    from_number = form_data.get("From", "")
    to_number = form_data.get("To", "")
    
    logger.info(
        "twilio_voice_callback",
        call_sid=call_sid,
        status=call_status,
        from_number=from_number,
    )
    
    # Log for voice receptionist agent
    audit = AuditLogModel()
    await audit.log_event(
        salon_id="system",  # Will be resolved from to_number
        event_type=AuditEventType.EXTERNAL_CALL,
        severity=AuditSeverity.INFO,
        actor=from_number,
        action=f"Voice call {call_status}",
        resource_type="call",
        resource_id=call_sid,
        details={
            "call_status": call_status,
            "from": from_number,
            "to": to_number,
        },
    )
    
    return PlainTextResponse("OK", status_code=200)
