# Twilio Omnichannel Communication Strategy

## Overview
Salon_Flow uses Twilio for cost-effective, scalable omnichannel customer communications across WhatsApp, SMS, and future voice channels. This guide ensures efficient usage aligned with our event-driven, serverless architecture.

## Architecture Principles

### 1. Unified Conversation State
Use **Twilio Conversations API** to maintain a single conversation thread across channels:
- Customer can start on WhatsApp, continue via SMS, without context loss
- All messages stored in one conversation resource
- Seamless handoff between automated AI and human agents

### 2. Event-Driven Processing
```
Twilio Webhook → Pub/Sub Topic → Cloud Run Service → Response
```
- Webhooks receive incoming messages
- Pub/Sub decouples processing for scale-to-zero efficiency
- Async processing reduces Cloud Run instance time = cost savings

### 3. Channel Selection Logic
| Channel | Use Case | Cost Factor |
|---------|----------|-------------|
| WhatsApp | Rich media, templates, high engagement | Higher per-message |
| SMS | Fallback, urgent alerts, simple text | Lower per-message |
| Voice | Complex issues, elderly customers | Highest |

## Cost Optimization Strategies

### Message Segment Control (Critical)
Twilio charges per **message segment**, not per message:

**GSM-7 Encoding** (160 chars/segment):
- Standard English letters, numbers, common symbols
- Cost: ~₹0.05-0.15 per segment

**UCS-2 Encoding** (70 chars/segment):
- Emojis, non-Latin scripts (Hindi, Telugu)
- Cost: ~2.3x more expensive

**Best Practices:**
```python
# ❌ Expensive - uses emojis, exceeds 160 chars
message = "🎉 Hi Rajesh! Your booking is confirmed for tomorrow at 2 PM! 🕐 See you soon! 💇‍♂️"
# Result: 2-3 segments with UCS-2 encoding

# ✅ Cost-effective - plain text, under 160 chars
message = "Hi Rajesh! Your booking is confirmed for tomorrow at 2 PM. See you soon!"
# Result: 1 segment with GSM-7 encoding
```

### Template-Based Messaging
Use **Twilio Content Template Builder** for:
- Pre-approved WhatsApp templates (required for outbound)
- Consistent formatting
- Reduced development time
- Compliance with WhatsApp policies

**Template Categories:**
1. **Booking Confirmations**: `booking_confirmation`
2. **Reminders**: `appointment_reminder`
3. **Promotions**: `promotional_offer`
4. **Feedback**: `feedback_request`

### Smart Routing
```python
# Route based on customer preference and cost
async def send_message(customer_id: str, message: str, priority: str = "normal"):
    customer = await get_customer(customer_id)
    
    # High priority = WhatsApp for read receipts
    if priority == "high" and customer.whatsapp_opt_in:
        return await send_whatsapp(customer.whatsapp_number, message)
    
    # Normal priority = SMS for cost savings
    elif customer.sms_consent:
        return await send_sms(customer.phone, message)
    
    # Fallback to WhatsApp if no SMS consent
    elif customer.whatsapp_opt_in:
        return await send_whatsapp(customer.whatsapp_number, message)
```

## Implementation Patterns

### 1. Webhook Handler (Cloud Run)
```python
# services/notification/app/webhooks/twilio.py
from fastapi import FastAPI, Request
import xml.etree.ElementTree as ET

app = FastAPI()

@app.post("/webhook/twilio/whatsapp")
async def whatsapp_webhook(request: Request):
    """Handle incoming WhatsApp messages"""
    form_data = await request.form()
    
    # Publish to Pub/Sub for async processing
    await publish_to_pubsub(
        topic="whatsapp-incoming",
        data={
            "from": form_data.get("From"),
            "body": form_data.get("Body"),
            "message_sid": form_data.get("MessageSid"),
            "timestamp": datetime.utcnow().isoformat()
        }
    )
    
    # Return immediate TwiML response
    return Response(
        content="<Response></Response>",
        media_type="application/xml"
    )
```

### 2. Async Processor
```python
# services/notification/app/processors/message_processor.py
from google.cloud import pubsub_v1

async def process_incoming_message(message_data: dict):
    """Process message from Pub/Sub"""
    customer_phone = message_data["from"]
    message_body = message_data["body"]
    
    # Get or create conversation
    conversation = await get_or_create_conversation(customer_phone)
    
    # Route to appropriate handler
    if is_booking_intent(message_body):
        response = await handle_booking_request(customer_phone, message_body)
    elif is_cancellation(message_body):
        response = await handle_cancellation(customer_phone, message_body)
    else:
        # Route to AI agent
        response = await ai_agent.process(customer_phone, message_body)
    
    # Send response via optimal channel
    await send_message(customer_phone, response)
```

### 3. TwiML for Simple Responses
Use **TwiML Bins** or serverless functions for simple auto-responses:
```xml
<!-- TwiML Bin: Outside Business Hours -->
<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>
        Thank you for contacting us! Our salon is currently closed. 
        We'll respond during business hours (9 AM - 8 PM).
        For urgent bookings, call: +91-XXXX-XXXXXX
    </Message>
</Response>
```

## Multi-Language Support

### Language Detection & Routing
```python
# Detect language and route to appropriate agent
async def detect_and_route(phone: str, message: str):
    # Simple keyword detection for Indian languages
    hindi_keywords = ["नमस्ते", "बुकिंग", "समय"]
    telugu_keywords = ["నమస్కారం", "బుకింగ్", "సమయం"]
    
    if any(kw in message for kw in hindi_keywords):
        return await hindi_agent.process(phone, message)
    elif any(kw in message for kw in telugu_keywords):
        return await telugu_agent.process(phone, message)
    else:
        return await english_agent.process(phone, message)
```

### Transliteration for Cost Savings
Instead of sending Hindi in UCS-2 (expensive):
```python
# ❌ Expensive UCS-2
hindi_message = "नमस्ते, आपकी बुकिंग कन्फर्म हो गई है"

# ✅ Cost-effective transliteration
romanized = "Namaste, aapki booking confirm ho gayi hai"
```

## Monitoring & Analytics

### Key Metrics to Track
| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Cost per conversation | < ₹2.00 | > ₹3.00 |
| Message delivery rate | > 95% | < 90% |
| Response time | < 5s | > 10s |
| Segment per message | 1.2 avg | > 1.5 |

### Cost Dashboard Query
```python
# Daily cost analysis
async def get_daily_messaging_costs():
    return {
        "whatsapp_segments": await count_segments("whatsapp"),
        "sms_segments": await count_segments("sms"),
        "total_cost_inr": calculate_cost(),
        "cost_per_customer": calculate_cost_per_customer(),
        "optimization_opportunities": find_expensive_patterns()
    }
```

## Security & Compliance

### Opt-In Management
```python
# Strict opt-in tracking
class CustomerCommunicationPrefs:
    whatsapp_opt_in: bool = False
    whatsapp_opt_in_date: Optional[datetime]
    sms_consent: bool = False
    sms_consent_date: Optional[datetime]
    preferred_language: str = "en"
    
    async def update_consent(self, channel: str, consented: bool):
        if channel == "whatsapp":
            self.whatsapp_opt_in = consented
            self.whatsapp_opt_in_date = datetime.utcnow()
        # Log for compliance audit
        await log_consent_change(self.customer_id, channel, consented)
```

### Data Retention
- Message content: 30 days
- Metadata: 1 year
- Consent records: 7 years (regulatory)

## Testing Strategy

### Local Testing with Twilio Test Credentials
```python
# Use test credentials for local development
TWILIO_TEST_ACCOUNT_SID = "ACxxx"
TWILIO_TEST_AUTH_TOKEN = "xxx"

# Test numbers provided by Twilio
TEST_WHATSAPP_NUMBER = "whatsapp:+14155238886"  # Sandbox
```

### Integration Tests
```python
# tests/notification/test_twilio_integration.py
async def test_whatsapp_message_flow():
    # Send test message
    response = await send_whatsapp(TEST_NUMBER, "Test message")
    assert response.status == "queued"
    
    # Verify webhook received
    webhook_data = await wait_for_webhook(timeout=10)
    assert webhook_data["Body"] == "Test message"
```

## Deployment Checklist

- [ ] Twilio account with WhatsApp Business API approved
- [ ] Webhook URLs configured in Twilio Console
- [ ] Pub/Sub topics created for message queues
- [ ] Content templates submitted for WhatsApp approval
- [ ] Opt-in flows implemented for compliance
- [ ] Cost monitoring dashboard configured
- [ ] Fallback SMS routes configured
- [ ] Multi-language agents tested
- [ ] Rate limiting implemented (prevent spam)

## Cost Benchmarks (India Market)

| Channel | Per Message | Monthly Volume | Monthly Cost |
|---------|-------------|----------------|--------------|
| SMS | ₹0.05-0.15 | 10,000 | ₹500-1,500 |
| WhatsApp Session | ₹0.30-0.50 | 5,000 | ₹1,500-2,500 |
| WhatsApp Template | ₹0.20-0.40 | 3,000 | ₹600-1,200 |

**Target**: Keep messaging costs under ₹4,500/month at current scale

## References

- [Twilio Conversations API Docs](https://www.twilio.com/docs/conversations)
- [WhatsApp Business API Pricing](https://www.twilio.com/whatsapp/pricing/in)
- [Message Segment Calculator](https://twiliodeved.github.io/message-segment-calculator/)
- [Content Template Builder](https://www.twilio.com/docs/content)
