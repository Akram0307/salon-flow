"""Schemas for Salon Integration (Twilio BYOK) configuration."""
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator

from .base import FirestoreModel, TimestampMixin


class IntegrationMode(str, Enum):
    """Integration mode for Twilio."""
    PLATFORM = "platform"  # Use platform-provided Twilio subaccount
    BYOK = "byok"  # Bring Your Own Keys (salon's own Twilio account)


class IntegrationStatus(str, Enum):
    """Status of the integration."""
    ACTIVE = "active"
    PENDING = "pending"  # Credentials saved but not verified
    FAILED = "failed"  # Verification failed
    DISABLED = "disabled"


# ============================================================================
# Request Models
# ============================================================================

class TwilioConfigRequest(BaseModel):
    """Request to save Twilio BYOK configuration."""
    account_sid: str = Field(..., description="Twilio Account SID", min_length=34, max_length=34)
    auth_token: str = Field(..., description="Twilio Auth Token", min_length=32, max_length=32)
    whatsapp_number: str = Field(..., description="WhatsApp number in E.164 format")
    sms_number: Optional[str] = Field(None, description="SMS number in E.164 format (optional)")
    
    @field_validator('account_sid')
    @classmethod
    def validate_account_sid(cls, v: str) -> str:
        if not v.startswith('AC'):
            raise ValueError('Account SID must start with "AC"')
        return v
    
    @field_validator('whatsapp_number', 'sms_number')
    @classmethod
    def validate_phone_format(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        # Remove whatsapp: prefix if present
        v = v.replace('whatsapp:', '')
        # Ensure E.164 format
        if not v.startswith('+'):
            raise ValueError('Phone number must be in E.164 format (e.g., +91XXXXXXXXXX)')
        return v


class TwilioTestRequest(BaseModel):
    """Request to test Twilio configuration."""
    to_number: str = Field(..., description="Phone number to send test message to")
    
    @field_validator('to_number')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        v = v.replace('whatsapp:', '')
        if not v.startswith('+'):
            raise ValueError('Phone number must be in E.164 format')
        return v


class ProvisionNumberRequest(BaseModel):
    """Request to provision a platform Twilio number."""
    area_code: Optional[str] = Field(None, description="Preferred area code for the number")
    capabilities: list[str] = Field(default=["sms", "whatsapp"], description="Required capabilities")


# ============================================================================
# Response Models
# ============================================================================

class TwilioConfigResponse(BaseModel):
    """Response for Twilio configuration (sensitive fields masked)."""
    salon_id: str
    mode: IntegrationMode
    status: IntegrationStatus
    whatsapp_number: Optional[str] = None
    sms_number: Optional[str] = None
    account_sid_preview: Optional[str] = Field(None, description="Last 4 chars of Account SID")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @field_validator('account_sid_preview', mode='before')
    @classmethod
    def mask_sid(cls, v: Optional[str]) -> Optional[str]:
        if v and len(v) > 4:
            return f"****{v[-4:]}"
        return v


class TwilioTestResponse(BaseModel):
    """Response from testing Twilio configuration."""
    success: bool
    message: str
    message_sid: Optional[str] = None
    error: Optional[str] = None


class ProvisionNumberResponse(BaseModel):
    """Response from provisioning a platform number."""
    success: bool
    message: str
    phone_number: Optional[str] = None
    error: Optional[str] = None


class IntegrationStatusResponse(BaseModel):
    """Overall integration status for a salon."""
    twilio: Optional[TwilioConfigResponse] = None
    has_platform_access: bool = False
    platform_whatsapp_number: Optional[str] = None


# ============================================================================
# Firestore Model
# ============================================================================

class SalonIntegration(FirestoreModel, TimestampMixin):
    """Firestore model for salon integrations.
    
    Collection: salon_integrations
    Document ID: salon_id
    """
    salon_id: str = Field(..., description="Reference to the salon")
    
    # Twilio BYOK credentials (encrypted)
    twilio_account_sid: Optional[str] = Field(None, description="Encrypted Twilio Account SID")
    twilio_auth_token: Optional[str] = Field(None, description="Encrypted Twilio Auth Token")
    twilio_whatsapp_number: Optional[str] = Field(None, description="WhatsApp number")
    twilio_sms_number: Optional[str] = Field(None, description="SMS number")
    
    # Mode and Status
    mode: IntegrationMode = Field(default=IntegrationMode.PLATFORM)
    status: IntegrationStatus = Field(default=IntegrationStatus.PENDING)
    
    # Metadata
    last_verified_at: Optional[datetime] = Field(None, description="Last successful verification")
    verification_error: Optional[str] = Field(None, description="Last verification error")
    
    class Config:
        use_enum_values = True
