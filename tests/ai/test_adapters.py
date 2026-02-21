"""Tests for Hexagonal Architecture Adapters

Tests the channel adapters including:
- WebAdapter (HTTP/REST)
- WhatsAppAdapter (Twilio)
- VoiceAdapter (Twilio Voice)
- BaseAdapter interface
"""
import pytest
import sys
import os
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../services/ai'))


@pytest.fixture(autouse=True)
def mock_settings():
    """Mock settings for all tests"""
    with patch("app.core.config.get_settings") as mock:
        settings = MagicMock()
        settings.openrouter_api_key = "test-api-key"
        settings.openrouter_base_url = "https://openrouter.ai/api/v1"
        settings.default_model = "google/gemini-2.0-flash-exp:free"
        settings.fallback_model = "google/gemini-flash-1.5"
        settings.max_tokens = 4096
        settings.temperature = 0.7
        settings.redis_url = "redis://localhost:6379/2"
        settings.cache_ttl = 3600
        settings.enable_cache = False
        settings.enable_logging = False
        mock.return_value = settings
        yield settings


class TestBaseAdapter:
    """Test the BaseAdapter interface"""
    
    def test_base_adapter_exists(self):
        """Test that BaseAdapter class exists"""
        from app.adapters.base import BaseAdapter
        assert BaseAdapter is not None
    
    def test_base_adapter_has_required_methods(self):
        """Test that BaseAdapter has required abstract methods"""
        from app.adapters.base import BaseAdapter
        import inspect
        
        methods = [m[0] for m in inspect.getmembers(BaseAdapter)]
        
        # Should have normalize and format methods
        assert 'normalize' in methods
        assert 'format' in methods
    
    def test_channel_type_enum(self):
        """Test ChannelType enum"""
        from app.adapters.base import ChannelType
        
        assert ChannelType.WEB == "web"
        assert ChannelType.WHATSAPP == "whatsapp"
        assert ChannelType.VOICE == "voice"
    
    def test_adapter_request_model(self):
        """Test AdapterRequest model"""
        from app.adapters.base import AdapterRequest, ChannelType
        
        request = AdapterRequest(
            prompt="Book a haircut",
            channel=ChannelType.WEB,
            salon_id="salon_123"
        )
        
        assert request.prompt == "Book a haircut"
        assert request.channel == ChannelType.WEB
        assert request.salon_id == "salon_123"
    
    def test_adapter_response_model(self):
        """Test AdapterResponse model"""
        from app.adapters.base import AdapterResponse
        
        response = AdapterResponse(
            message="I can help you book",
            success=True,
            agent_used="booking"
        )
        
        assert response.success is True
        assert response.message == "I can help you book"
        assert response.agent_used == "booking"


class TestWebAdapter:
    """Test the Web/HTTP Adapter"""
    
    @pytest.fixture
    def adapter(self):
        """Create WebAdapter instance"""
        from app.adapters.web_adapter import WebAdapter
        return WebAdapter()
    
    def test_web_adapter_channel(self, adapter):
        """Test web adapter channel type"""
        from app.adapters.base import ChannelType
        assert adapter.channel == ChannelType.WEB
    
    @pytest.mark.asyncio
    async def test_web_adapter_normalize(self, adapter):
        """Test web adapter request normalization"""
        raw_request = {
            "prompt": "Book a haircut",
            "salon_id": "salon_123",
            "user_id": "user_456",
            "language": "en"
        }
        
        result = await adapter.normalize(raw_request)
        
        assert result.prompt == "Book a haircut"
        assert result.channel == "web"
        assert result.salon_id == "salon_123"
    
    @pytest.mark.asyncio
    async def test_web_adapter_normalize_with_message_field(self, adapter):
        """Test normalization with 'message' field instead of 'prompt'"""
        raw_request = {
            "message": "I need a haircut",
            "salon_id": "salon_123"
        }
        
        result = await adapter.normalize(raw_request)
        assert result.prompt == "I need a haircut"
    
    @pytest.mark.asyncio
    async def test_web_adapter_normalize_with_query_field(self, adapter):
        """Test normalization with 'query' field"""
        raw_request = {
            "query": "What services do you offer?",
            "salon_id": "salon_123"
        }
        
        result = await adapter.normalize(raw_request)
        assert result.prompt == "What services do you offer?"
    
    @pytest.mark.asyncio
    async def test_web_adapter_normalize_missing_prompt(self, adapter):
        """Test normalization with missing prompt"""
        from app.adapters.base import AdapterError
        
        raw_request = {
            "salon_id": "salon_123"
        }
        
        with pytest.raises(AdapterError):
            await adapter.normalize(raw_request)
    
    @pytest.mark.asyncio
    async def test_web_adapter_normalize_with_attachments(self, adapter):
        """Test normalization with image attachments"""
        raw_request = {
            "prompt": "What hairstyle suits me?",
            "salon_id": "salon_123",
            "image_url": "https://example.com/image.jpg"
        }
        
        result = await adapter.normalize(raw_request)
        assert len(result.attachments) == 1
        assert result.attachments[0]["type"] == "image"
    
    @pytest.mark.asyncio
    async def test_web_adapter_normalize_with_history(self, adapter):
        """Test normalization with conversation history"""
        raw_request = {
            "prompt": "Book that for tomorrow",
            "salon_id": "salon_123",
            "history": [
                {"role": "user", "content": "I want a haircut"},
                {"role": "assistant", "content": "Sure, when?"}
            ]
        }
        
        result = await adapter.normalize(raw_request)
        assert "history" in result.metadata
        assert len(result.metadata["history"]) == 2
    
    @pytest.mark.asyncio
    async def test_web_adapter_format(self, adapter):
        """Test web adapter response formatting"""
        from app.adapters.base import AdapterResponse
        
        response = AdapterResponse(
            message="I can help you book a haircut",
            success=True,
            data={"slots": ["2 PM", "3 PM"]},
            agent_used="booking",
            cached=False
        )
        
        result = await adapter.format(response)
        
        assert result["success"] is True
        assert result["message"] == "I can help you book a haircut"
        assert "metadata" in result
    
    @pytest.mark.asyncio
    async def test_web_adapter_format_error_response(self, adapter):
        """Test formatting error response"""
        from app.adapters.base import AdapterResponse
        
        response = AdapterResponse(
            message="Query blocked by guardrail",
            success=False,
            blocked=True
        )
        
        result = await adapter.format(response)
        
        assert result["success"] is False
        assert "error" in result
    
    @pytest.mark.asyncio
    async def test_web_adapter_validate_auth_with_bearer(self, adapter):
        """Test auth validation with Bearer token"""
        raw_request = {
            "prompt": "Test",
            "authorization": "Bearer valid_token"
        }
        
        result = await adapter.validate_auth(raw_request)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_web_adapter_validate_auth_with_api_key(self, adapter):
        """Test auth validation with API key"""
        raw_request = {
            "prompt": "Test",
            "api_key": "valid_api_key"
        }
        
        result = await adapter.validate_auth(raw_request)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_web_adapter_validate_auth_with_salon_id(self, adapter):
        """Test auth validation with salon_id fallback"""
        raw_request = {
            "prompt": "Test",
            "salon_id": "salon_123"
        }
        
        result = await adapter.validate_auth(raw_request)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_web_adapter_health_check(self, adapter):
        """Test web adapter health check"""
        result = await adapter.health_check()
        assert result is True


class TestWhatsAppAdapter:
    """Test the WhatsApp Adapter"""
    
    @pytest.fixture
    def adapter(self):
        """Create WhatsAppAdapter instance"""
        from app.adapters.whatsapp_adapter import WhatsAppAdapter
        return WhatsAppAdapter(
            twilio_account_sid="test_sid",
            twilio_auth_token="test_token",
            twilio_phone_number="+14155238886"
        )
    
    def test_whatsapp_adapter_channel(self, adapter):
        """Test WhatsApp adapter channel type"""
        from app.adapters.base import ChannelType
        assert adapter.channel == ChannelType.WHATSAPP
    
    @pytest.mark.asyncio
    async def test_whatsapp_adapter_normalize(self, adapter):
        """Test WhatsApp adapter request normalization"""
        raw_request = {
            "Body": "Book a haircut for tomorrow",
            "From": "whatsapp:+919876543210",
            "To": "whatsapp:+14155238886",
            "MessageSid": "SM123456"
        }
        
        result = await adapter.normalize(raw_request)
        
        assert result.prompt == "Book a haircut for tomorrow"
        assert result.channel == "whatsapp"
        assert "919876543210" in result.metadata.get("from_number", "")
    
    @pytest.mark.asyncio
    async def test_whatsapp_adapter_normalize_with_media(self, adapter):
        """Test normalization with media attachments"""
        raw_request = {
            "Body": "What hairstyle suits me?",
            "From": "whatsapp:+919876543210",
            "NumMedia": "1",
            "MediaUrl0": "https://example.com/image.jpg",
            "MediaContentType0": "image/jpeg"
        }
        
        result = await adapter.normalize(raw_request)
        assert len(result.attachments) == 1
        assert result.attachments[0]["type"] == "image"
    
    @pytest.mark.asyncio
    async def test_whatsapp_adapter_normalize_with_location(self, adapter):
        """Test normalization with location sharing"""
        raw_request = {
            "Body": "",
            "From": "whatsapp:+919876543210",
            "Latitude": "17.3850",
            "Longitude": "78.4867"
        }
        
        result = await adapter.normalize(raw_request)
        # Should have location attachment
        location_attachments = [a for a in result.attachments if a.get("type") == "location"]
        assert len(location_attachments) == 1
    
    @pytest.mark.asyncio
    async def test_whatsapp_adapter_normalize_button_response(self, adapter):
        """Test normalization with button response"""
        raw_request = {
            "Body": "",
            "From": "whatsapp:+919876543210",
            "ButtonPayload": "book_haircut"
        }
        
        result = await adapter.normalize(raw_request)
        assert result.prompt == "book_haircut"
        assert result.metadata.get("button_response") is True
    
    @pytest.mark.asyncio
    async def test_whatsapp_adapter_detect_language_hindi(self, adapter):
        """Test Hindi language detection"""
        raw_request = {
            "Body": "मुझे हेयरकट बुक करनी है",
            "From": "whatsapp:+919876543210"
        }
        
        result = await adapter.normalize(raw_request)
        assert result.language == "hi"
    
    @pytest.mark.asyncio
    async def test_whatsapp_adapter_detect_language_telugu(self, adapter):
        """Test Telugu language detection"""
        raw_request = {
            "Body": "నాకు హెయిర్‌కట్ కావాలి",
            "From": "whatsapp:+919876543210"
        }
        
        result = await adapter.normalize(raw_request)
        assert result.language == "te"
    
    @pytest.mark.asyncio
    async def test_whatsapp_adapter_format(self, adapter):
        """Test WhatsApp adapter response formatting"""
        from app.adapters.base import AdapterResponse
        
        response = AdapterResponse(
            message="Your appointment is confirmed",
            success=True,
            agent_used="booking"
        )
        
        result = await adapter.format(response)
        
        assert result["type"] == "text"
        assert result["text"]["body"] == "Your appointment is confirmed"
    
    @pytest.mark.asyncio
    async def test_whatsapp_adapter_format_with_suggestions(self, adapter):
        """Test formatting with suggestions as buttons"""
        from app.adapters.base import AdapterResponse
        
        response = AdapterResponse(
            message="Choose a time slot",
            success=True,
            suggestions=["2 PM", "3 PM", "4 PM"]
        )
        
        result = await adapter.format(response)
        
        # Should be interactive with buttons
        assert result["type"] == "interactive"
        assert "interactive" in result
    
    @pytest.mark.asyncio
    async def test_whatsapp_adapter_format_with_image(self, adapter):
        """Test formatting with image"""
        from app.adapters.base import AdapterResponse
        
        response = AdapterResponse(
            message="Check out our new style",
            success=True
        )
        
        result = await adapter.format_with_image(
            response,
            image_url="https://example.com/style.jpg",
            caption="New hairstyle"
        )
        
        assert result["type"] == "image"
        assert result["image"]["link"] == "https://example.com/style.jpg"
    
    @pytest.mark.asyncio
    async def test_whatsapp_adapter_format_list(self, adapter):
        """Test formatting as interactive list"""
        from app.adapters.base import AdapterResponse
        
        response = AdapterResponse(
            message="Select a service",
            success=True,
            agent_used="booking"
        )
        
        sections = [{
            "title": "Hair Services",
            "rows": [
                {"id": "haircut", "title": "Haircut"},
                {"id": "color", "title": "Hair Color"}
            ]
        }]
        
        result = await adapter.format_list(response, sections)
        
        assert result["type"] == "interactive"
        assert result["interactive"]["type"] == "list"


class TestVoiceAdapter:
    """Test the Voice Adapter"""
    
    @pytest.fixture
    def adapter(self):
        """Create VoiceAdapter instance"""
        from app.adapters.voice_adapter import VoiceAdapter
        return VoiceAdapter(
            twilio_account_sid="test_sid",
            twilio_auth_token="test_token",
            twilio_phone_number="+14155238886"
        )
    
    def test_voice_adapter_channel(self, adapter):
        """Test voice adapter channel type"""
        from app.adapters.base import ChannelType
        assert adapter.channel == ChannelType.VOICE
    
    @pytest.mark.asyncio
    async def test_voice_adapter_normalize_initial_call(self, adapter):
        """Test normalization for initial call"""
        raw_request = {
            "CallSid": "CA123456",
            "From": "+919876543210",
            "To": "+14155238886",
            "CallStatus": "ringing"
        }
        
        result = await adapter.normalize(raw_request)
        
        assert result.prompt == "[CALL_START]"
        assert result.channel == "voice"
        assert result.metadata.get("is_initial_call") is True
    
    @pytest.mark.asyncio
    async def test_voice_adapter_normalize_with_speech(self, adapter):
        """Test normalization with speech input"""
        raw_request = {
            "CallSid": "CA123456",
            "From": "+919876543210",
            "SpeechResult": "I want to book a haircut",
            "Confidence": "0.85"
        }
        
        result = await adapter.normalize(raw_request)
        
        assert result.prompt == "I want to book a haircut"
        assert result.metadata.get("confidence") == "0.85"
    
    @pytest.mark.asyncio
    async def test_voice_adapter_normalize_with_digits(self, adapter):
        """Test normalization with DTMF digits"""
        raw_request = {
            "CallSid": "CA123456",
            "From": "+919876543210",
            "Digits": "1"
        }
        
        result = await adapter.normalize(raw_request)
        assert result.prompt == "1"
    
    @pytest.mark.asyncio
    async def test_voice_adapter_format(self, adapter):
        """Test voice adapter response formatting (TwiML)"""
        from app.adapters.base import AdapterResponse
        
        response = AdapterResponse(
            message="Welcome to our salon. How can I help you?",
            success=True,
            agent_used="voice_receptionist"
        )
        
        result = await adapter.format(response)
        
        assert "twiml" in result
        assert "<?xml" in result["twiml"]
        assert "<Response>" in result["twiml"]
        assert "<Say" in result["twiml"]
    
    @pytest.mark.asyncio
    async def test_voice_adapter_format_with_suggestions(self, adapter):
        """Test formatting with IVR suggestions"""
        from app.adapters.base import AdapterResponse
        
        response = AdapterResponse(
            message="Press a number",
            success=True,
            suggestions=["Book appointment", "Check status", "Speak to staff"]
        )
        
        result = await adapter.format(response)
        
        assert "<Gather" in result["twiml"]
    
    @pytest.mark.asyncio
    async def test_voice_adapter_format_blocked(self, adapter):
        """Test formatting blocked response"""
        from app.adapters.base import AdapterResponse
        
        response = AdapterResponse(
            message="Query not allowed",
            success=False,
            blocked=True
        )
        
        result = await adapter.format(response)
        
        assert "<Hangup/>" in result["twiml"]
    
    @pytest.mark.asyncio
    async def test_voice_adapter_format_gather(self, adapter):
        """Test formatting IVR gather menu"""
        result = await adapter.format_gather(
            prompt="Press 1 for booking, 2 for support",
            options=["Booking", "Support", "Hours"],
            timeout=5
        )
        
        assert "<Gather" in result["twiml"]
        assert "timeout=\"5\"" in result["twiml"]
    
    @pytest.mark.asyncio
    async def test_voice_adapter_format_transfer(self, adapter):
        """Test formatting call transfer"""
        result = await adapter.format_transfer(
            transfer_number="+919876543210",
            message="Transferring to our stylist"
        )
        
        assert "<Dial>" in result["twiml"]
        assert "+919876543210" in result["twiml"]
    
    @pytest.mark.asyncio
    async def test_voice_adapter_xml_escaping(self, adapter):
        """Test XML special character escaping"""
        escaped = adapter._escape_xml("Hello & welcome to <Salon>")
        
        assert "&amp;" in escaped
        assert "&lt;" in escaped
        assert "&gt;" in escaped


class TestAdapterIntegration:
    """Test adapter integration scenarios"""
    
    @pytest.mark.asyncio
    async def test_web_to_agent_flow(self, mock_settings):
        """Test complete flow from web adapter to agent"""
        from app.adapters.web_adapter import WebAdapter
        from app.adapters.base import AdapterResponse
        
        adapter = WebAdapter()
        
        # Normalize request
        normalized = await adapter.normalize({
            "prompt": "Book a haircut",
            "salon_id": "salon_123"
        })
        
        assert normalized.prompt == "Book a haircut"
        
        # Format response
        response = AdapterResponse(
            message="Booking confirmed",
            success=True
        )
        
        formatted = await adapter.format(response)
        assert formatted["success"] is True
    
    @pytest.mark.asyncio
    async def test_whatsapp_to_agent_flow(self, mock_settings):
        """Test complete flow from WhatsApp adapter to agent"""
        from app.adapters.whatsapp_adapter import WhatsAppAdapter
        from app.adapters.base import AdapterResponse
        
        adapter = WhatsAppAdapter()
        
        # Normalize request
        normalized = await adapter.normalize({
            "Body": "Book haircut",
            "From": "whatsapp:+919876543210"
        })
        
        assert normalized.prompt == "Book haircut"
        
        # Format response
        response = AdapterResponse(
            message="Booking confirmed",
            success=True,
            suggestions=["2 PM", "3 PM"]
        )
        
        formatted = await adapter.format(response)
        assert formatted["type"] in ["text", "interactive"]
    
    @pytest.mark.asyncio
    async def test_voice_to_agent_flow(self, mock_settings):
        """Test complete flow from voice adapter to agent"""
        from app.adapters.voice_adapter import VoiceAdapter
        from app.adapters.base import AdapterResponse
        
        adapter = VoiceAdapter()
        
        # Normalize request
        normalized = await adapter.normalize({
            "CallSid": "CA123",
            "From": "+919876543210",
            "SpeechResult": "Book haircut"
        })
        
        assert normalized.prompt == "Book haircut"
        
        # Format response
        response = AdapterResponse(
            message="Booking confirmed",
            success=True
        )
        
        formatted = await adapter.format(response)
        assert "twiml" in formatted


class TestAdapterErrorHandling:
    """Test adapter error handling"""
    
    @pytest.mark.asyncio
    async def test_web_adapter_malformed_request(self):
        """Test web adapter with malformed request"""
        from app.adapters.web_adapter import WebAdapter
        from app.adapters.base import AdapterError
        
        adapter = WebAdapter()
        
        with pytest.raises(AdapterError):
            await adapter.normalize({})  # Missing prompt
    
    @pytest.mark.asyncio
    async def test_whatsapp_adapter_empty_body(self):
        """Test WhatsApp adapter with empty body"""
        from app.adapters.whatsapp_adapter import WhatsAppAdapter
        
        adapter = WhatsAppAdapter()
        
        result = await adapter.normalize({
            "Body": "",
            "From": "whatsapp:+919876543210"
        })
        
        # Should handle gracefully
        assert result.prompt == ""
    
    @pytest.mark.asyncio
    async def test_voice_adapter_missing_call_sid(self):
        """Test voice adapter with missing call SID"""
        from app.adapters.voice_adapter import VoiceAdapter
        
        adapter = VoiceAdapter()
        
        result = await adapter.normalize({
            "From": "+919876543210"
        })
        
        # Should handle gracefully
        assert result.channel == "voice"


# Run tests with: pytest tests/ai/test_adapters.py -v
