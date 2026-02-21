"""Hexagonal Adapters for Multi-Channel Support

Implements the Hexagonal (Ports & Adapters) architecture for:
- Web/HTTP requests (PWAs)
- WhatsApp messages (Twilio)
- Voice calls (Twilio Programmable Voice)

Each adapter normalizes channel-specific requests to a common format
and formats responses appropriately for each channel.

Usage:
    from app.adapters import WebAdapter, WhatsAppAdapter, VoiceAdapter
    
    # Web channel
    web_adapter = WebAdapter()
    request = await web_adapter.normalize(http_request)
    response = await web_adapter.format(ai_response)
    
    # WhatsApp channel
    wa_adapter = WhatsAppAdapter()
    request = await wa_adapter.normalize(twilio_webhook)
    response = await wa_adapter.format(ai_response)
    
    # Voice channel
    voice_adapter = VoiceAdapter()
    request = await voice_adapter.normalize(voice_webhook)
    twiml = await voice_adapter.format(ai_response)
"""
from .base import (
    BaseAdapter,
    ChannelType,
    AdapterRequest,
    AdapterResponse,
    AdapterError,
    AuthenticationError,
    MediaProcessingError,
)
from .web_adapter import WebAdapter, StreamingWebAdapter
from .whatsapp_adapter import WhatsAppAdapter
from .voice_adapter import VoiceAdapter, VoiceSession

__all__ = [
    # Base classes
    "BaseAdapter",
    "ChannelType",
    "AdapterRequest",
    "AdapterResponse",
    # Exceptions
    "AdapterError",
    "AuthenticationError",
    "MediaProcessingError",
    # Adapters
    "WebAdapter",
    "StreamingWebAdapter",
    "WhatsAppAdapter",
    "VoiceAdapter",
    "VoiceSession",
]
