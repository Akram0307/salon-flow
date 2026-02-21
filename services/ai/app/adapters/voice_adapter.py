"""Voice Adapter for Telephony Integration

Handles voice calls via Twilio Programmable Voice or similar services.
Supports speech-to-text, text-to-speech, and IVR flows.
"""
from typing import Dict, Any, Optional, List
import structlog
from datetime import datetime
import hashlib
import asyncio

from .base import (
    BaseAdapter,
    ChannelType,
    AdapterRequest,
    AdapterResponse,
    AdapterError,
)

logger = structlog.get_logger()


class VoiceAdapter(BaseAdapter):
    """Adapter for Voice channel via Twilio.
    
    Handles:
    - Incoming voice calls
    - Speech-to-text transcription
    - Text-to-speech response synthesis
    - IVR menu navigation
    - Call recording and logging
    
    Example:
        adapter = VoiceAdapter()
        
        # Normalize incoming call webhook
        request = await adapter.normalize(twilio_voice_webhook)
        
        # Format response as TwiML
        twiml = await adapter.format(response)
    """
    
    def __init__(
        self,
        twilio_account_sid: Optional[str] = None,
        twilio_auth_token: Optional[str] = None,
        twilio_phone_number: Optional[str] = None,
        default_language: str = "en-IN",
        default_voice: str = "Polly.Aditi"
    ):
        self._account_sid = twilio_account_sid
        self._auth_token = twilio_auth_token
        self._phone_number = twilio_phone_number
        self._default_language = default_language
        self._default_voice = default_voice
        self._client = None
    
    @property
    def channel(self) -> ChannelType:
        return ChannelType.VOICE
    
    def _get_twilio_client(self):
        """Get or create Twilio client."""
        if self._client is None and self._account_sid and self._auth_token:
            from twilio.rest import Client
            self._client = Client(self._account_sid, self._auth_token)
        return self._client
    
    async def normalize(self, raw_request: Dict[str, Any]) -> AdapterRequest:
        """Normalize Twilio Voice webhook to AdapterRequest.
        
        Args:
            raw_request: Twilio voice webhook data
            
        Returns:
            Normalized AdapterRequest
        """
        try:
            # Extract caller information
            from_number = raw_request.get("From", "")
            caller_phone = from_number.replace("tel:", "") if from_number else None
            
            # Generate user_id from phone number
            user_id = hashlib.sha256(caller_phone.encode()).hexdigest()[:16] if caller_phone else None
            
            # Extract salon_id from called number
            to_number = raw_request.get("To", "")
            salon_id = self._extract_salon_id(to_number, raw_request)
            
            # Extract speech input (if from Gather)
            prompt = raw_request.get("SpeechResult", "") or raw_request.get("Digits", "")
            
            # If no speech result, this is initial call - use greeting intent
            if not prompt:
                prompt = "[CALL_START]"
            
            # Detect language from speech or use default
            language = self._detect_language_from_speech(raw_request)
            
            # Build conversation ID from call SID
            call_sid = raw_request.get("CallSid", "")
            conversation_id = f"voice_{call_sid}" if call_sid else None
            
            # Build metadata
            metadata = {
                "call_sid": call_sid,
                "call_status": raw_request.get("CallStatus"),
                "call_duration": raw_request.get("CallDuration"),
                "from_number": caller_phone,
                "to_number": to_number,
                "forwarded_from": raw_request.get("ForwardedFrom"),
                "caller_name": raw_request.get("CallerName"),
                "recording_url": raw_request.get("RecordingUrl"),
                "transcription_text": raw_request.get("TranscriptionText"),
                "confidence": raw_request.get("Confidence"),
                "is_initial_call": prompt == "[CALL_START]",
            }
            
            return AdapterRequest(
                prompt=prompt,
                channel=ChannelType.VOICE,
                salon_id=salon_id,
                user_id=user_id,
                session_id=conversation_id,
                conversation_id=conversation_id,
                language=language,
                locale=f"{language}-IN",
                raw_data=raw_request,
                attachments=[],
                metadata=metadata
            )
            
        except Exception as e:
            raise AdapterError(
                channel=self.channel.value,
                message=f"Failed to normalize voice request: {str(e)}"
            )
    
    def _extract_salon_id(self, to_number: str, raw_request: Dict) -> Optional[str]:
        """Extract salon ID from called number.
        
        In production, this would map phone numbers to salons.
        """
        if raw_request.get("salon_id"):
            return raw_request.get("salon_id")
        return "default_salon"
    
    def _detect_language_from_speech(self, raw_request: Dict) -> str:
        """Detect language from speech input.
        
        Uses confidence scores and speech patterns.
        """
        # Check for explicit language parameter
        if raw_request.get("language"):
            return raw_request.get("language")
        
        # Analyze speech result for language patterns
        speech = raw_request.get("SpeechResult", "")
        
        # Simple heuristics for Indian languages
        telugu_chars = sum(1 for c in speech if '\u0C00' <= c <= '\u0C7F')
        hindi_chars = sum(1 for c in speech if '\u0900' <= c <= '\u097F')
        
        if telugu_chars > len(speech) * 0.3:
            return "te"
        if hindi_chars > len(speech) * 0.3:
            return "hi"
        
        return "en"
    
    async def format(self, response: AdapterResponse) -> Dict[str, Any]:
        """Format response as TwiML for voice.
        
        Args:
            response: Normalized response from AI service
            
        Returns:
            TwiML-formatted response
        """
        # Build TwiML response
        twiml_parts = ['<?xml version="1.0" encoding="UTF-8"?>']
        twiml_parts.append('<Response>')
        
        # Add pause for natural feel
        twiml_parts.append('<Pause length="1"/>')
        
        # Add main response as speech
        message = response.message
        
        # Configure TTS
        twiml_parts.append(
            f'<Say language="{self._default_language}" voice="{self._default_voice}">'
            f'{self._escape_xml(message)}'
            f'</Say>'
        )
        
        # Add suggestions as Gather (for IVR)
        if response.suggestions:
            twiml_parts.append('<Gather input="speech dtmf" timeout="5" numDigits="1">')
            twiml_parts.append(
                f'<Say language="{self._default_language}" voice="{self._default_voice}">'
                f'Press or say: {". ".join(str(i+1) + " for " + s for i, s in enumerate(response.suggestions[:4]))}'
                f'</Say>'
            )
            twiml_parts.append('</Gather>')
        
        # Add hangup or redirect
        if response.blocked:
            twiml_parts.append('<Say>Thank you for calling. Goodbye.</Say>')
            twiml_parts.append('<Hangup/>')
        else:
            # Continue conversation
            twiml_parts.append('<Redirect>./continue</Redirect>')
        
        twiml_parts.append('</Response>')
        
        return {
            "twiml": "\n".join(twiml_parts),
            "content_type": "application/xml",
            "metadata": {
                "agent": response.agent_used,
                "cached": response.cached,
                "blocked": response.blocked
            }
        }
    
    def _escape_xml(self, text: str) -> str:
        """Escape special characters for XML."""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;")
        )
    
    async def format_gather(
        self,
        prompt: str,
        options: List[str],
        timeout: int = 5
    ) -> Dict[str, Any]:
        """Format IVR gather menu.
        
        Args:
            prompt: Menu prompt
            options: List of menu options
            timeout: Timeout in seconds
            
        Returns:
            TwiML with Gather
        """
        twiml_parts = ['<?xml version="1.0" encoding="UTF-8"?>']
        twiml_parts.append('<Response>')
        twiml_parts.append(f'<Gather input="speech dtmf" timeout="{timeout}" numDigits="1">')
        twiml_parts.append(
            f'<Say language="{self._default_language}" voice="{self._default_voice}">'
            f'{self._escape_xml(prompt)}'
            f'</Say>'
        )
        
        for i, option in enumerate(options[:9]):
            twiml_parts.append(
                f'<Say language="{self._default_language}" voice="{self._default_voice}">'
                f'Press {i+1} for {self._escape_xml(option)}'
                f'</Say>'
            )
        
        twiml_parts.append('</Gather>')
        twiml_parts.append('<Say>No input received. Goodbye.</Say>')
        twiml_parts.append('<Hangup/>')
        twiml_parts.append('</Response>')
        
        return {
            "twiml": "\n".join(twiml_parts),
            "content_type": "application/xml"
        }
    
    async def format_transfer(
        self,
        transfer_number: str,
        message: str = "Transferring your call"
    ) -> Dict[str, Any]:
        """Format call transfer TwiML.
        
        Args:
            transfer_number: Number to transfer to
            message: Transfer message
            
        Returns:
            TwiML with Dial
        """
        twiml_parts = ['<?xml version="1.0" encoding="UTF-8"?>']
        twiml_parts.append('<Response>')
        twiml_parts.append(
            f'<Say language="{self._default_language}" voice="{self._default_voice}">'
            f'{self._escape_xml(message)}'
            f'</Say>'
        )
        twiml_parts.append(f'<Dial>{transfer_number}</Dial>')
        twiml_parts.append('</Response>')
        
        return {
            "twiml": "\n".join(twiml_parts),
            "content_type": "application/xml"
        }
    
    async def validate_auth(self, raw_request: Dict[str, Any]) -> bool:
        """Validate Twilio voice webhook signature.
        
        Args:
            raw_request: Raw webhook request
            
        Returns:
            True if authenticated
        """
        if not self._auth_token:
            return True
        
        # Validate Twilio signature
        # Similar to WhatsApp adapter
        return True
    
    async def handle_media(self, raw_request: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle voice recordings.
        
        Args:
            raw_request: Request with recording URL
            
        Returns:
            List with recording info
        """
        attachments = []
        
        if raw_request.get("RecordingUrl"):
            attachments.append({
                "type": "audio",
                "url": raw_request["RecordingUrl"],
                "duration": raw_request.get("RecordingDuration")
            })
        
        return attachments
    
    async def send_response(
        self,
        formatted_response: Dict[str, Any],
        raw_request: Dict[str, Any]
    ) -> bool:
        """Send TwiML response.
        
        For voice, this is typically returned directly in the webhook response.
        
        Args:
            formatted_response: TwiML response
            raw_request: Original request
            
        Returns:
            True (TwiML is returned in webhook response)
        """
        return True
    
    async def transcribe_recording(self, recording_url: str) -> str:
        """Transcribe a voice recording.
        
        Args:
            recording_url: URL of the recording
            
        Returns:
            Transcription text
        """
        try:
            # Use Google Speech-to-Text or similar
            # This is a placeholder implementation
            logger.info("transcribing_recording", url=recording_url)
            return "[Transcription placeholder]"
        except Exception as e:
            logger.error("transcription_failed", error=str(e))
            return ""
    
    async def health_check(self) -> bool:
        """Check Twilio connection health.
        
        Returns:
            True if healthy
        """
        if not self._account_sid or not self._auth_token:
            return False
        
        try:
            client = self._get_twilio_client()
            account = client.api.accounts(self._account_sid).fetch()
            return account.status == "active"
        except Exception as e:
            logger.warning("voice_health_check_failed", error=str(e))
            return False


class VoiceSession:
    """Manages a voice call session state.
    
    Tracks:
    - Call progress
    - Menu navigation
    - Conversation history
    """
    
    def __init__(self, call_sid: str, salon_id: str):
        self.call_sid = call_sid
        self.salon_id = salon_id
        self.state = "greeting"
        self.history: List[Dict[str, str]] = []
        self.menu_stack: List[str] = []
        self.start_time = datetime.utcnow()
    
    def add_interaction(self, user_input: str, response: str) -> None:
        """Add an interaction to history."""
        self.history.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.utcnow().isoformat()
        })
        self.history.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def get_context(self) -> Dict[str, Any]:
        """Get session context."""
        return {
            "call_sid": self.call_sid,
            "salon_id": self.salon_id,
            "state": self.state,
            "history": self.history[-10:],  # Last 10 interactions
            "duration_seconds": (datetime.utcnow() - self.start_time).total_seconds()
        }
