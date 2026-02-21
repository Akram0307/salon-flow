"""Base Adapter Interface for Hexagonal Architecture

Implements the Hexagonal (Ports & Adapters) pattern for multi-channel support.
Each channel (Web, WhatsApp, Voice) has its own adapter that normalizes
requests to a common format.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class ChannelType(str, Enum):
    """Supported communication channels"""
    WEB = "web"
    WHATSAPP = "whatsapp"
    VOICE = "voice"


class AdapterRequest(BaseModel):
    """Normalized request from any channel"""
    # Core fields
    prompt: str = Field(..., description="User message/prompt")
    channel: ChannelType = Field(..., description="Source channel")
    
    # Context fields
    salon_id: Optional[str] = Field(None, description="Salon identifier")
    user_id: Optional[str] = Field(None, description="User identifier")
    session_id: Optional[str] = Field(None, description="Session identifier")
    conversation_id: Optional[str] = Field(None, description="Conversation thread ID")
    
    # Language and locale
    language: str = Field(default="en", description="User language preference")
    locale: str = Field(default="en-IN", description="User locale")
    
    # Channel-specific data
    raw_data: Dict[str, Any] = Field(default_factory=dict, description="Raw channel data")
    attachments: List[Dict[str, Any]] = Field(default_factory=list, description="Attachments (images, files)")
    
    # Metadata
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = {"use_enum_values": True}


class AdapterResponse(BaseModel):
    """Normalized response for any channel"""
    # Core response
    message: str = Field(..., description="Response message")
    success: bool = Field(default=True, description="Whether request succeeded")
    
    # Structured data
    data: Optional[Dict[str, Any]] = Field(None, description="Structured response data")
    suggestions: List[str] = Field(default_factory=list, description="Follow-up suggestions")
    
    # Channel-specific formatting
    formatted_response: Optional[Dict[str, Any]] = Field(None, description="Channel-formatted response")
    
    # Metadata
    agent_used: Optional[str] = Field(None, description="Agent that processed request")
    model_used: Optional[str] = Field(None, description="Model used")
    cached: bool = Field(default=False, description="Whether from cache")
    blocked: bool = Field(default=False, description="Whether blocked by guardrail")
    execution_time_ms: Optional[float] = Field(None, description="Execution time")
    
    model_config = {"use_enum_values": True}


class BaseAdapter(ABC):
    """Base class for channel adapters.
    
    Each adapter handles:
    1. Incoming request normalization
    2. Outgoing response formatting
    3. Channel-specific authentication
    4. Media handling (images, audio, etc.)
    
    Example:
        class WhatsAppAdapter(BaseAdapter):
            def normalize(self, raw_request: Dict) -> AdapterRequest:
                # Convert Twilio webhook to AdapterRequest
                pass
            
            def format(self, response: AdapterResponse) -> Dict:
                # Convert AdapterResponse to Twilio message format
                pass
    """
    
    @property
    @abstractmethod
    def channel(self) -> ChannelType:
        """Return the channel type this adapter handles"""
        pass
    
    @abstractmethod
    async def normalize(self, raw_request: Dict[str, Any]) -> AdapterRequest:
        """Normalize incoming channel-specific request to common format.
        
        Args:
            raw_request: Raw request from the channel
            
        Returns:
            Normalized AdapterRequest
        """
        pass
    
    @abstractmethod
    async def format(self, response: AdapterResponse) -> Dict[str, Any]:
        """Format normalized response for the channel.
        
        Args:
            response: Normalized response from AI service
            
        Returns:
            Channel-specific formatted response
        """
        pass
    
    async def validate_auth(self, raw_request: Dict[str, Any]) -> bool:
        """Validate channel-specific authentication.
        
        Args:
            raw_request: Raw request to validate
            
        Returns:
            True if authenticated, False otherwise
        """
        return True
    
    async def handle_media(self, raw_request: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract and process media attachments.
        
        Args:
            raw_request: Raw request containing media
            
        Returns:
            List of processed attachments
        """
        return []
    
    async def send_response(
        self,
        formatted_response: Dict[str, Any],
        raw_request: Dict[str, Any]
    ) -> bool:
        """Send formatted response back through the channel.
        
        Args:
            formatted_response: Channel-formatted response
            raw_request: Original raw request (for reply context)
            
        Returns:
            True if sent successfully
        """
        return True
    
    def get_conversation_history(
        self,
        conversation_id: str,
        limit: int = 10
    ) -> List[Dict[str, str]]:
        """Retrieve conversation history for context.
        
        Args:
            conversation_id: Conversation identifier
            limit: Maximum messages to retrieve
            
        Returns:
            List of conversation messages
        """
        return []
    
    async def health_check(self) -> bool:
        """Check adapter health status.
        
        Returns:
            True if healthy
        """
        return True


class AdapterError(Exception):
    """Error in adapter processing"""
    def __init__(
        self,
        channel: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        self.channel = channel
        self.message = message
        self.details = details or {}
        super().__init__(f"{channel} adapter error: {message}")


class AuthenticationError(AdapterError):
    """Authentication error in adapter"""
    pass


class MediaProcessingError(AdapterError):
    """Error processing media"""
    pass
