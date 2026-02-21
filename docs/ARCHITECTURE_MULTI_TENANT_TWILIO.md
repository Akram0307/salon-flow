# Multi-Tenant Twilio Architecture Recommendation
## Salon Flow SaaS Platform

**Document Version:** 1.0  
**Date:** February 2026  
**Author:** Senior Solutions Architect

---

## Executive Summary

This document provides a comprehensive architectural recommendation for enabling per-salon Twilio configuration in the Salon Flow multi-tenant SaaS platform. After analyzing the existing codebase, adapters, and data models, **I recommend a Hybrid Approach (Option C)** that balances flexibility, security, and operational simplicity.

---

## 1. Architecture Options Analysis

### Option A: Bring Your Own Account (BYOA)

Each salon owner configures their own Twilio account.

#### Architecture Diagram
```
┌─────────────────────────────────────────────────────────────────┐
│                      Salon Flow Platform                         │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  Salon A    │  │  Salon B    │  │  Salon C    │              │
│  │  Twilio #1  │  │  Twilio #2  │  │  Twilio #3  │              │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘              │
│         │                │                │                     │
│         ▼                ▼                ▼                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Credential Manager Service                  │   │
│  │   • Encrypt/Decrypt per-salon credentials                │   │
│  │   • Route requests to correct Twilio account            │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
         │                │                │
         ▼                ▼                ▼
    ┌─────────┐     ┌─────────┐     ┌─────────┐
    │Twilio A │     │Twilio B │     │Twilio C │
    │(Owner)  │     │(Owner)  │     │(Owner)  │
    └─────────┘     └─────────┘     └─────────┘
```

#### Pros
| Benefit | Description |
|---------|-------------|
| **Cost Transparency** | Each salon pays their own Twilio bill directly |
| **No Middleman** | Salon owners have direct access to Twilio console |
| **Independence** | Salon can switch platforms without losing phone number |
| **Compliance** | Easier GDPR/data ownership per salon |
| **Scalability** | No platform-level rate limits per Twilio account |

#### Cons
| Drawback | Description |
|----------|-------------|
| **Onboarding Complexity** | Salon owners must create Twilio account, get number, configure webhooks |
| **Support Burden** | Platform must help with Twilio issues outside their control |
| **Inconsistent Features** | Some salons may not have WhatsApp-enabled numbers |
| **Webhook Management** | Each salon must configure webhook URLs correctly |
| **Number Portability** | If salon leaves, they keep their number (good for them, bad for platform lock-in) |

#### Implementation Complexity: **HIGH**

---

### Option B: Platform-Level Twilio with Subaccounts

Platform owns one Twilio account with subaccounts per salon.

#### Architecture Diagram
```
┌─────────────────────────────────────────────────────────────────┐
│                      Salon Flow Platform                         │
├─────────────────────────────────────────────────────────────────┤
│                     ┌─────────────────┐                         │
│                     │  Master Twilio  │                         │
│                     │    Account      │                         │
│                     └────────┬────────┘                         │
│                              │                                   │
│         ┌────────────────────┼────────────────────┐             │
│         │                    │                    │             │
│         ▼                    ▼                    ▼             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ Subaccount  │  │ Subaccount  │  │ Subaccount  │              │
│  │  Salon A    │  │  Salon B    │  │  Salon C    │              │
│  │ +9198765432 │  │ +9198765433 │  │ +9198765434 │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  Single Twilio  │
                    │    Console      │
                    │  (Platform)     │
                    └─────────────────┘
```

#### Pros
| Benefit | Description |
|---------|-------------|
| **Simplified Onboarding** | Platform provisions number for salon automatically |
| **Centralized Management** | All numbers in one Twilio console |
| **Consistent Features** | All salons get same WhatsApp/Voice capabilities |
| **Webhook Simplicity** | Single webhook URL for all salons |
| **Usage Analytics** | Easy to track per-salon usage |
| **Bulk Operations** | Apply changes across all salons |

#### Cons
| Drawback | Description |
|----------|-------------|
| **Platform Bears Cost** | Platform must bill salons for usage |
| **Rate Limits** | Single account = shared rate limits |
| **Compliance Risk** | Platform responsible for all messaging compliance |
| **Number Lock-in** | If salon leaves, they lose their number |
| **Twilio Pricing** | Higher tier may be needed for volume |

#### Implementation Complexity: **MEDIUM**

---

### Option C: Hybrid Approach (RECOMMENDED)

Platform provides default Twilio, salons can optionally bring their own.

#### Architecture Diagram
```
┌─────────────────────────────────────────────────────────────────┐
│                      Salon Flow Platform                         │
├─────────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                  Communication Router                      │  │
│  │   • Route to salon's Twilio or platform default           │  │
│  │   • Handle credential resolution                           │  │
│  │   • Track usage per salon                                  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              │                                   │
│         ┌────────────────────┴────────────────────┐             │
│         │                                         │             │
│         ▼                                         ▼             │
│  ┌─────────────────┐                    ┌─────────────────┐     │
│  │  Platform-Level │                    │   BYOA Salons   │     │
│  │    Twilio       │                    │                 │     │
│  │  (Subaccounts)  │                    │  ┌───────────┐  │     │
│  │                 │                    │  │ Salon X   │  │     │
│  │  ┌───────────┐  │                    │  │ Twilio #X │  │     │
│  │  │ Salon A   │  │                    │  └───────────┘  │     │
│  │  │ Subaccount│  │                    │  ┌───────────┐  │     │
│  │  └───────────┘  │                    │  │ Salon Y   │  │     │
│  │  ┌───────────┐  │                    │  │ Twilio #Y │  │     │
│  │  │ Salon B   │  │                    │  └───────────┘  │     │
│  │  │ Subaccount│  │                    │                 │     │
│  │  └───────────┘  │                    └─────────────────┘     │
│  └─────────────────┘                                             │
└─────────────────────────────────────────────────────────────────┘
```

#### Pros
| Benefit | Description |
|---------|-------------|
| **Best of Both Worlds** | Combines benefits of Options A and B |
| **Flexible Onboarding** | Quick start with platform default, migrate to BYOA later |
| **Graceful Degradation** | Platform default ensures no salon is without messaging |
| **Scalability** | Heavy users can offload to their own accounts |
| **Revenue Opportunity** | Platform can markup platform-level messaging |
| **Customer Choice** | Enterprise salons can use their own Twilio |

#### Cons
| Drawback | Description |
|----------|-------------|
| **Implementation Complexity** | More code paths to maintain |
| **Testing Overhead** | Must test both scenarios |
| **Documentation** | Need docs for both paths |

#### Implementation Complexity: **MEDIUM-HIGH**

---

## 2. Security Considerations

### 2.1 Credential Storage Strategy

#### Recommendation: Hybrid Approach

```
┌─────────────────────────────────────────────────────────────────┐
│                    Credential Storage Strategy                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Platform-Level Credentials (Default)                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  GCP Secret Manager                                      │   │
│  │  • twilio-account-sid (platform default)                 │   │
│  │  • twilio-auth-token (platform default)                  │   │
│  │  • twilio-phone-number (platform default)                │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  Per-Salon Credentials (BYOA)                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Firestore (Encrypted)                                   │   │
│  │  Collection: salon_integrations                          │   │
│  │  Document: {salon_id}                                    │   │
│  │  Fields:                                                 │   │
│  │    • twilio_account_sid (AES-256-GCM encrypted)         │   │
│  │    • twilio_auth_token (AES-256-GCM encrypted)          │   │
│  │    • twilio_phone_number (plaintext)                    │   │
│  │    • encryption_key_ref (KMS key reference)             │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### Why Firestore for Per-Salon Credentials?

| Factor | GCP Secret Manager | Firestore (Encrypted) |
|--------|-------------------|----------------------|
| **Scalability** | Limited secrets quota | Unlimited documents |
| **Cost** | $0.06/secret/month + operations | Included in Firestore costs |
| **Access Control** | IAM per secret | Firestore rules + KMS |
| **Audit** | Cloud Audit Logs | Firestore audit + KMS |
| **Recommendation** | Platform-level only | Per-salon credentials |

### 2.2 Encryption Implementation

```python
# services/api/app/services/credential_encryption.py

from google.cloud import kms_v1
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import base64
import os


class CredentialEncryption:
    """Encrypt/decrypt sensitive credentials using GCP KMS + AES-256-GCM."""
    
    def __init__(self, project_id: str, key_ring_id: str, key_id: str):
        self.kms_client = kms_v1.KeyManagementServiceClient()
        self.key_name = self.kms_client.crypto_key_path(
            project_id, "global", key_ring_id, key_id
        )
    
    def encrypt(self, plaintext: str) -> dict:
        """Encrypt credential using envelope encryption.
        
        Returns dict with:
        - ciphertext: base64-encoded encrypted data
        - data_key: KMS-encrypted data encryption key
        - nonce: base64-encoded nonce
        """
        # Generate data encryption key (DEK)
        dek = os.urandom(32)  # 256-bit key
        nonce = os.urandom(12)  # 96-bit nonce for GCM
        
        # Encrypt DEK with KMS
        kms_response = self.kms_client.encrypt(
            request={"name": self.key_name, "plaintext": dek}
        )
        encrypted_dek = kms_response.ciphertext
        
        # Encrypt plaintext with DEK
        aesgcm = AESGCM(dek)
        ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), None)
        
        return {
            "ciphertext": base64.b64encode(ciphertext).decode(),
            "data_key": base64.b64encode(encrypted_dek).decode(),
            "nonce": base64.b64encode(nonce).decode(),
        }
    
    def decrypt(self, encrypted_data: dict) -> str:
        """Decrypt credential using envelope encryption."""
        # Decrypt DEK with KMS
        encrypted_dek = base64.b64decode(encrypted_data["data_key"])
        kms_response = self.kms_client.decrypt(
            request={"name": self.key_name, "ciphertext": encrypted_dek}
        )
        dek = kms_response.plaintext
        
        # Decrypt ciphertext with DEK
        nonce = base64.b64decode(encrypted_data["nonce"])
        ciphertext = base64.b64decode(encrypted_data["ciphertext"])
        
        aesgcm = AESGCM(dek)
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        
        return plaintext.decode()
```

### 2.3 Credential Rotation Strategy

```
┌─────────────────────────────────────────────────────────────────┐
│                  Credential Rotation Workflow                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. Platform-Level Credentials                                  │
│     ┌─────────────────────────────────────────────────────┐     │
│     │  • Rotate every 90 days (automated)                  │     │
│     │  • Use GCP Secret Manager versioning                 │     │
│     │  • Update Cloud Run environment variables            │     │
│     │  • Zero-downtime rotation via dual credentials       │     │
│     └─────────────────────────────────────────────────────┘     │
│                                                                  │
│  2. Per-Salon Credentials (BYOA)                                │
│     ┌─────────────────────────────────────────────────────┐     │
│     │  • Salon owner initiates rotation in dashboard       │     │
│     │  • Platform validates new credentials                │     │
│     │  • Old credentials retained for 24h rollback         │     │
│     │  • Audit log entry for rotation                      │     │
│     └─────────────────────────────────────────────────────┘     │
│                                                                  │
│  3. Rotation Notification                                       │
│     ┌─────────────────────────────────────────────────────┐     │
│     │  • Email notification on credential change           │     │
│     │  • Slack/webhook alert for security team             │     │
│     │  • Dashboard banner showing last rotation date       │     │
│     └─────────────────────────────────────────────────────┘     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Data Model Changes

### 3.1 New Schema: SalonIntegration

```python
# services/api/app/schemas/integration.py

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import Field, field_validator
from .base import FirestoreModel, TimestampMixin


class TwilioConfig(FirestoreModel):
    """Twilio configuration for a salon."""
    
    # Account credentials (encrypted)
    account_sid: Optional[Dict[str, str]] = Field(
        default=None,
        description="Encrypted Twilio Account SID"
    )
    auth_token: Optional[Dict[str, str]] = Field(
        default=None,
        description="Encrypted Twilio Auth Token"
    )
    
    # Phone numbers
    phone_number: Optional[str] = Field(
        default=None,
        description="Twilio phone number (E.164 format)"
    )
    whatsapp_number: Optional[str] = Field(
        default=None,
        description="WhatsApp Business number (E.164 format)"
    )
    
    # Mode
    mode: str = Field(
        default="sandbox",
        description="'sandbox' or 'production'"
    )
    
    # Status
    is_active: bool = Field(default=False)
    is_verified: bool = Field(default=False)
    verification_status: str = Field(
        default="pending",
        description="pending, verified, failed"
    )
    
    # Capabilities
    capabilities: Dict[str, bool] = Field(
        default_factory=lambda: {
            "voice": False,
            "sms": False,
            "whatsapp": False,
            "mms": False
        }
    )
    
    # Webhook configuration
    webhook_base_url: Optional[str] = Field(
        default=None,
        description="Base URL for Twilio webhooks"
    )
    webhook_status: str = Field(
        default="not_configured",
        description="not_configured, configured, error"
    )
    
    # Usage tracking
    usage: Dict[str, Any] = Field(
        default_factory=lambda: {
            "messages_sent": 0,
            "messages_received": 0,
            "calls_made": 0,
            "calls_received": 0,
            "whatsapp_sent": 0,
            "whatsapp_received": 0,
            "last_updated": None
        }
    )
    
    # Billing
    billing_mode: str = Field(
        default="platform",
        description="'platform' or 'own_account'"
    )
    
    # Timestamps
    configured_at: Optional[datetime] = None
    verified_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    
    @field_validator('phone_number', 'whatsapp_number')
    @classmethod
    def validate_phone_format(cls, v: Optional[str]) -> Optional[str]:
        if v and not v.startswith('+'):
            raise ValueError("Phone number must be in E.164 format (+countrycode...)")
        return v


class SalonIntegration(FirestoreModel, TimestampMixin):
    """Integration settings for a salon."""
    
    salon_id: str = Field(..., description="Reference to salon")
    
    # Communication integrations
    twilio: TwilioConfig = Field(default_factory=TwilioConfig)
    
    # Future integrations (extensible)
    email: Optional[Dict[str, Any]] = None  # SendGrid, Mailgun, etc.
    payment: Optional[Dict[str, Any]] = None  # Razorpay, Stripe, etc.
    analytics: Optional[Dict[str, Any]] = None  # Google Analytics, etc.
    
    # Integration status
    status: str = Field(
        default="not_configured",
        description="not_configured, partial, active, error"
    )
    
    # Audit
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
```

### 3.2 Updated SalonSettings Schema

```python
# Add to existing SalonSettings schema

class CommunicationSettings(FirestoreModel):
    """Communication channel settings."""
    
    # Channel preferences
    primary_channel: str = Field(
        default="whatsapp",
        description="Primary communication channel"
    )
    fallback_channel: str = Field(
        default="sms",
        description="Fallback if primary fails"
    )
    
    # WhatsApp settings
    whatsapp_enabled: bool = Field(default=True)
    whatsapp_greeting: Optional[str] = Field(
        default="Welcome to {salon_name}! How can I help you today?"
    )
    whatsapp_business_hours_only: bool = Field(default=True)
    
    # Voice settings
    voice_enabled: bool = Field(default=True)
    voice_greeting: Optional[str] = Field(
        default="Thank you for calling {salon_name}. Press 1 to book, 2 for hours."
    )
    voice_transfer_number: Optional[str] = None
    voice_business_hours_only: bool = Field(default=True)
    
    # SMS settings
    sms_enabled: bool = Field(default=True)
    sms_sender_id: Optional[str] = None
    
    # Language settings
    default_language: str = Field(default="en")
    supported_languages: list = Field(
        default_factory=lambda: ["en", "hi", "te"]
    )
```

### 3.3 Firestore Collection Structure

```
firestore/
├── salons/                          # Existing collection
│   └── {salon_id}/
│       └── ... (existing fields)
│
├── salon_integrations/              # NEW collection
│   └── {salon_id}/                  # Document ID = salon_id
│       ├── twilio: {...}
│       ├── email: {...}
│       ├── payment: {...}
│       └── status: "active"
│
├── integration_usage/               # NEW collection
│   └── {salon_id}_{month}/          # e.g., salon123_2026-02
│       ├── twilio_messages: 1234
│       ├── twilio_calls: 56
│       ├── twilio_whatsapp: 789
│       └── estimated_cost: 45.67
│
└── integration_audit/               # NEW collection
    └── {audit_id}/
        ├── salon_id: "..."
        ├── action: "credential_update"
        ├── timestamp: "..."
        └── actor: "..."
```

---

## 4. Cost & Billing Strategy

### 4.1 Cost Allocation Model

```
┌─────────────────────────────────────────────────────────────────┐
│                    Cost & Billing Model                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Platform-Provided Twilio (Default)                             │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Pricing Model:                                          │   │
│  │  • Base subscription includes: 500 messages/month        │   │
│  │  • Overage: ₹0.50/message (WhatsApp), ₹0.20/SMS          │   │
│  │  • Voice: ₹0.10/minute                                   │   │
│  │                                                          │   │
│  │  Platform Markup:                                        │   │
│  │  • 15% markup on Twilio costs                            │   │
│  │  • Covers: Support, infrastructure, compliance           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  BYOA (Bring Your Own Account)                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Pricing Model:                                          │   │
│  │  • No platform messaging fees                            │   │
│  │  • Salon pays Twilio directly                            │   │
│  │  • Platform subscription unchanged                       │   │
│  │                                                          │   │
│  │  Platform Value-Add:                                     │   │
│  │  • Integration support: ₹500 one-time setup              │   │
│  │  • Ongoing webhook management: included                  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Usage Tracking Implementation

```python
# services/api/app/services/usage_tracker.py

from datetime import datetime, date
from typing import Dict, Any
import structlog

logger = structlog.get_logger()


class UsageTracker:
    """Track and bill communication usage per salon."""
    
    # Twilio pricing (approximate, in INR)
    PRICING = {
        "whatsapp_outbound": 0.50,  # Per message
        "whatsapp_inbound": 0.00,   # Free
        "sms_outbound": 0.20,       # Per segment
        "sms_inbound": 0.00,
        "voice_inbound": 0.10,      # Per minute
        "voice_outbound": 0.15,     # Per minute
    }
    
    async def record_usage(
        self,
        salon_id: str,
        channel: str,
        direction: str,
        quantity: int = 1,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Record usage for billing.
        
        Args:
            salon_id: Salon identifier
            channel: 'whatsapp', 'sms', 'voice'
            direction: 'inbound' or 'outbound'
            quantity: Number of units
            metadata: Additional info (message_sid, duration, etc.)
        
        Returns:
            Usage record with cost calculation
        """
        month_key = date.today().strftime("%Y-%m")
        usage_key = f"{channel}_{direction}"
        
        # Calculate cost
        unit_cost = self.PRICING.get(usage_key, 0)
        total_cost = unit_cost * quantity
        
        # Record to Firestore
        usage_ref = self.db.collection("integration_usage").document(
            f"{salon_id}_{month_key}"
        )
        
        await usage_ref.set({
            usage_key: increment(quantity),
            f"{usage_key}_cost": increment(total_cost),
            "total_cost": increment(total_cost),
            "last_updated": datetime.utcnow(),
        }, merge=True)
        
        return {
            "salon_id": salon_id,
            "usage_type": usage_key,
            "quantity": quantity,
            "unit_cost": unit_cost,
            "total_cost": total_cost,
            "month": month_key,
        }
```

---

## 5. Fallback Strategy

### 5.1 Fallback Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│                    Fallback Strategy                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  When Salon Has No Twilio Configured:                           │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  1. Check salon_integrations.twilio.is_active           │   │
│  │     ↓ NO                                                 │   │
│  │  2. Use Platform Default Twilio (Subaccount)            │   │
│  │     ↓                                                    │   │
│  │  3. Create subaccount for salon (lazy provisioning)     │   │
│  │     ↓                                                    │   │
│  │  4. Assign platform phone number from pool              │   │
│  │     ↓                                                    │   │
│  │  5. Configure webhooks automatically                    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  When Salon's Twilio Fails:                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  1. Log error with context                               │   │
│  │  2. Retry with exponential backoff (3 attempts)          │   │
│  │  3. If still failing:                                    │   │
│  │     a. Queue message for retry                           │   │
│  │     b. Notify salon admin via email                      │   │
│  │     c. Update integration status to 'error'              │   │
│  │  4. If critical (booking confirmation):                  │   │
│  │     a. Fall back to SMS via platform default             │   │
│  │     b. Or email notification                             │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 Fallback Implementation

```python
# services/ai/app/services/communication_router.py

from typing import Optional, Dict, Any
import structlog

from app.adapters.whatsapp_adapter import WhatsAppAdapter
from app.adapters.voice_adapter import VoiceAdapter

logger = structlog.get_logger()


class CommunicationRouter:
    """Route communications to correct Twilio account."""
    
    def __init__(
        self,
        platform_twilio_sid: str,
        platform_twilio_token: str,
        platform_twilio_phone: str,
    ):
        self.platform_credentials = {
            "account_sid": platform_twilio_sid,
            "auth_token": platform_twilio_token,
            "phone_number": platform_twilio_phone,
        }
    
    async def get_adapter(
        self,
        salon_id: str,
        channel: str,
        salon_integration: Optional[Dict] = None
    ) -> tuple:
        """Get appropriate adapter for salon.
        
        Returns:
            Tuple of (adapter, credentials_source)
        """
        # Check if salon has own Twilio configured
        if salon_integration and salon_integration.get("twilio", {}).get("is_active"):
            twilio_config = salon_integration["twilio"]
            
            # Decrypt credentials
            credentials = await self._decrypt_credentials(twilio_config)
            
            if channel == "whatsapp":
                adapter = WhatsAppAdapter(
                    twilio_account_sid=credentials["account_sid"],
                    twilio_auth_token=credentials["auth_token"],
                    twilio_phone_number=credentials.get("whatsapp_number") or credentials.get("phone_number"),
                )
            else:
                adapter = VoiceAdapter(
                    twilio_account_sid=credentials["account_sid"],
                    twilio_auth_token=credentials["auth_token"],
                    twilio_phone_number=credentials.get("phone_number"),
                )
            
            return adapter, "salon_own"
        
        # Fall back to platform default
        logger.info(
            "using_platform_default_twilio",
            salon_id=salon_id,
            channel=channel
        )
        
        # Get or create subaccount for salon
        subaccount = await self._get_or_create_subaccount(salon_id)
        
        if channel == "whatsapp":
            adapter = WhatsAppAdapter(
                twilio_account_sid=subaccount["account_sid"],
                twilio_auth_token=subaccount["auth_token"],
                twilio_phone_number=subaccount["phone_number"],
            )
        else:
            adapter = VoiceAdapter(
                twilio_account_sid=subaccount["account_sid"],
                twilio_auth_token=subaccount["auth_token"],
                twilio_phone_number=subaccount["phone_number"],
            )
        
        return adapter, "platform_subaccount"
```

---

## 6. Onboarding Flow

### 6.1 Salon Owner Setup Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    Onboarding Flow                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Step 1: Dashboard Settings                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Salon Owner navigates to:                               │   │
│  │  Settings → Integrations → Communication                 │   │
│  │                                                          │   │
│  │  Options presented:                                      │   │
│  │  ○ Use Platform Messaging (Recommended)                  │   │
│  │  ○ Configure My Own Twilio Account                       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│  Step 2A: Platform Messaging (Default)                          │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  1. Click "Enable Messaging"                             │   │
│  │  2. Platform auto-provisions:                            │   │
│  │     • Twilio subaccount                                  │   │
│  │     • Phone number (from pool)                           │   │
│  │     • WhatsApp sandbox (or production if approved)       │   │
│  │  3. Webhook auto-configured                              │   │
│  │  4. Test message sent to salon owner                     │   │
│  │  5. ✅ Ready to use in 30 seconds                        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  Step 2B: BYOA (Bring Your Own Account)                         │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  1. Click "Configure My Twilio"                          │   │
│  │  2. Modal shows requirements:                            │   │
│  │     □ Twilio Account (free to create)                    │   │
│  │     □ Phone number purchased (~$1/month)                 │   │
│  │     □ WhatsApp Business API approved (for WhatsApp)      │   │
│  │                                                          │   │
│  │  3. Enter credentials:                                   │   │
│  │     ┌─────────────────────────────────────────────┐      │   │
│  │     │ Account SID: [________________________]     │      │   │
│  │     │ Auth Token: [________________________]     │      │   │
│  │     │ Phone Number: [+_____________________]     │      │   │
│  │     │ WhatsApp Number: [+_________________]      │      │   │
│  │     │ Mode: [Sandbox ▼]                          │      │   │
│  │     └─────────────────────────────────────────────┘      │   │
│  │                                                          │   │
│  │  4. Platform validates credentials                       │   │
│  │  5. Platform configures webhooks automatically          │   │
│  │  6. Test message sent                                    │   │
│  │  7. ✅ Ready to use                                       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 6.2 Webhook Auto-Configuration

```python
# services/api/app/services/twilio_webhook_config.py

from typing import Dict, Any
import structlog

logger = structlog.get_logger()


class TwilioWebhookConfig:
    """Auto-configure Twilio webhooks for salons."""
    
    WEBHOOK_BASE = "https://api.salonflow.ai/webhooks/twilio"
    
    async def configure_webhooks(
        self,
        account_sid: str,
        auth_token: str,
        salon_id: str,
    ) -> Dict[str, Any]:
        """Configure webhooks for a salon's Twilio account."""
        from twilio.rest import Client
        
        client = Client(account_sid, auth_token)
        
        # Webhook URLs
        webhook_urls = {
            "voice": f"{self.WEBHOOK_BASE}/voice/{salon_id}",
            "sms": f"{self.WEBHOOK_BASE}/sms/{salon_id}",
            "whatsapp": f"{self.WEBHOOK_BASE}/whatsapp/{salon_id}",
            "status": f"{self.WEBHOOK_BASE}/status/{salon_id}",
        }
        
        results = {}
        
        # Configure each phone number
        numbers = client.incoming_phone_numbers.list()
        for number in numbers:
            number.update(
                voice_url=webhook_urls["voice"],
                voice_method="POST",
                sms_url=webhook_urls["sms"],
                sms_method="POST",
                status_callback=webhook_urls["status"],
                status_callback_method="POST",
            )
            results[number.phone_number] = "configured"
        
        return {
            "status": "configured",
            "webhook_urls": webhook_urls,
            "numbers_configured": len(results),
        }
```

---

## 7. Implementation Roadmap

### Phase 1: Foundation (Week 1-2)

| Task | Description | Priority |
|------|-------------|----------|
| Create `SalonIntegration` schema | New Firestore collection | HIGH |
| Implement `CredentialEncryption` | KMS + AES-256-GCM | HIGH |
| Create `CommunicationRouter` | Route to correct Twilio | HIGH |
| Update adapters | Support dynamic credentials | HIGH |

### Phase 2: Platform Default (Week 3-4)

| Task | Description | Priority |
|------|-------------|----------|
| Implement subaccount provisioning | Auto-create Twilio subaccounts | HIGH |
| Phone number pool management | Reserve numbers for salons | MEDIUM |
| Webhook auto-configuration | Configure on provisioning | HIGH |
| Usage tracking | Record per-salon usage | MEDIUM |

### Phase 3: BYOA Support (Week 5-6)

| Task | Description | Priority |
|------|-------------|----------|
| Dashboard UI for Twilio config | Settings page integration | HIGH |
| Credential validation | Test credentials before saving | HIGH |
| Webhook configuration for BYOA | Auto-configure salon's webhooks | HIGH |
| Sandbox mode support | Handle Twilio sandbox | MEDIUM |

### Phase 4: Billing & Monitoring (Week 7-8)

| Task | Description | Priority |
|------|-------------|----------|
| Usage-based billing | Track and bill per salon | MEDIUM |
| Cost dashboard | Show salon owners their usage | LOW |
| Alert system | Notify on issues | MEDIUM |
| Audit logging | Track all credential changes | HIGH |

---

## 8. Security Checklist

- [ ] All credentials encrypted at rest (AES-256-GCM)
- [ ] Encryption keys managed by GCP KMS
- [ ] Credentials never logged or exposed in errors
- [ ] Webhook signature validation enabled
- [ ] Rate limiting per salon
- [ ] Audit trail for all credential changes
- [ ] IP allowlisting for Twilio webhooks
- [ ] Credential rotation reminders
- [ ] SOC 2 compliance documentation
- [ ] GDPR data handling procedures

---

## 9. Summary Recommendation

### Recommended Approach: **Hybrid (Option C)**

| Aspect | Recommendation |
|--------|---------------|
| **Default** | Platform-provided Twilio with subaccounts |
| **Advanced** | BYOA for enterprise/large salons |
| **Storage** | GCP Secret Manager (platform) + Firestore encrypted (per-salon) |
| **Encryption** | GCP KMS + AES-256-GCM envelope encryption |
| **Billing** | Usage-based with platform markup |
| **Fallback** | Platform default always available |
| **Onboarding** | 30-second setup for platform, guided flow for BYOA |

### Key Benefits

1. **Low Barrier to Entry**: New salons can start messaging in 30 seconds
2. **Enterprise Flexibility**: Large salons can use their own Twilio
3. **Revenue Opportunity**: Platform markup on messaging
4. **Scalability**: Heavy users offload to their own accounts
5. **Reliability**: Platform default ensures no salon is without messaging

---

**Document End**
