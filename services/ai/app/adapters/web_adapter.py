"""Web/HTTP Adapter for REST API Requests

Handles requests from the frontend PWAs (Owner, Manager, Staff, Client).
Normalizes HTTP requests to the common AdapterRequest format.
"""
from typing import Dict, Any, Optional, List
import structlog
from datetime import datetime

from .base import (
    BaseAdapter,
    ChannelType,
    AdapterRequest,
    AdapterResponse,
    AdapterError,
)

logger = structlog.get_logger()


class WebAdapter(BaseAdapter):
    """Adapter for Web/HTTP channel requests.
    
    Handles requests from:
    - Owner PWA (admin dashboard)
    - Manager PWA (analytics, staff management)
    - Staff PWA (appointments, services)
    - Client PWA (booking, profile)
    
    Example:
        adapter = WebAdapter()
        
        # Normalize incoming HTTP request
        request = await adapter.normalize({
            "prompt": "Book a haircut for tomorrow",
            "salon_id": "salon_123",
            "user_id": "user_456",
            "language": "en"
        })
        
        # Format response for HTTP
        formatted = await adapter.format(response)
    """
    
    def __init__(self):
        self._supported_content_types = ["application/json", "multipart/form-data"]
    
    @property
    def channel(self) -> ChannelType:
        return ChannelType.WEB
    
    async def normalize(self, raw_request: Dict[str, Any]) -> AdapterRequest:
        """Normalize HTTP request to AdapterRequest.
        
        Args:
            raw_request: Raw HTTP request data
            
        Returns:
            Normalized AdapterRequest
            
        Raises:
            AdapterError: If required fields are missing
        """
        try:
            # Extract core prompt
            prompt = raw_request.get("prompt") or raw_request.get("message") or raw_request.get("query", "")
            
            if not prompt:
                raise AdapterError(
                    channel=self.channel.value,
                    message="Missing required field: prompt/message/query"
                )
            
            # Extract context
            salon_id = raw_request.get("salon_id") or raw_request.get("tenant_id")
            user_id = raw_request.get("user_id") or raw_request.get("uid")
            session_id = raw_request.get("session_id") or raw_request.get("conversation_id")
            
            # Extract language preference
            language = raw_request.get("language", "en")
            locale = raw_request.get("locale", "en-IN")
            
            # Extract conversation history if provided
            history = raw_request.get("history", [])
            
            # Extract attachments (for image analysis)
            attachments = []
            if raw_request.get("image_url"):
                attachments.append({
                    "type": "image",
                    "url": raw_request["image_url"]
                })
            if raw_request.get("images"):
                for img in raw_request["images"]:
                    attachments.append({"type": "image", "url": img})
            
            # Build metadata
            metadata = {
                "source": raw_request.get("source", "pwa"),
                "user_agent": raw_request.get("user_agent"),
                "ip_address": raw_request.get("ip_address"),
                "history": history,
                "use_cache": raw_request.get("use_cache", True),
                "skip_guardrail": raw_request.get("skip_guardrail", False),
                "model_tier": raw_request.get("model_tier"),
                "stream": raw_request.get("stream", False),
            }
            
            return AdapterRequest(
                prompt=prompt,
                channel=ChannelType.WEB,
                salon_id=salon_id,
                user_id=user_id,
                session_id=session_id,
                conversation_id=raw_request.get("conversation_id"),
                language=language,
                locale=locale,
                raw_data=raw_request,
                attachments=attachments,
                metadata=metadata
            )
            
        except AdapterError:
            raise
        except Exception as e:
            raise AdapterError(
                channel=self.channel.value,
                message=f"Failed to normalize request: {str(e)}"
            )
    
    async def format(self, response: AdapterResponse) -> Dict[str, Any]:
        """Format response for HTTP/JSON.
        
        Args:
            response: Normalized response from AI service
            
        Returns:
            HTTP-formatted response dictionary
        """
        formatted = {
            "success": response.success,
            "message": response.message,
            "data": response.data,
            "suggestions": response.suggestions,
            "metadata": {
                "agent": response.agent_used,
                "model": response.model_used,
                "cached": response.cached,
                "blocked": response.blocked,
                "execution_time_ms": response.execution_time_ms,
            }
        }
        
        # Add error details if failed
        if not response.success:
            formatted["error"] = {
                "message": response.message,
                "blocked": response.blocked
            }
        
        return formatted
    
    async def validate_auth(self, raw_request: Dict[str, Any]) -> bool:
        """Validate HTTP authentication.
        
        Checks for valid Firebase Auth token or API key.
        
        Args:
            raw_request: Raw request with auth headers
            
        Returns:
            True if authenticated
        """
        # Check for authorization header
        auth_header = raw_request.get("authorization") or raw_request.get("Authorization")
        api_key = raw_request.get("api_key") or raw_request.get("x-api-key")
        
        if auth_header:
            # Validate Firebase JWT token
            # This would integrate with Firebase Auth
            return auth_header.startswith("Bearer ")
        
        if api_key:
            # Validate API key
            # This would check against stored API keys
            return len(api_key) > 0
        
        # Allow requests with salon_id for now (will be validated by backend)
        return raw_request.get("salon_id") is not None
    
    async def handle_media(self, raw_request: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract media from HTTP request.
        
        Handles:
        - Base64 encoded images
        - Image URLs
        - Uploaded files
        
        Args:
            raw_request: Request containing media
            
        Returns:
            List of processed attachments
        """
        attachments = []
        
        # Handle base64 images
        if raw_request.get("image_base64"):
            attachments.append({
                "type": "image",
                "data": raw_request["image_base64"],
                "encoding": "base64"
            })
        
        # Handle image URLs
        if raw_request.get("image_url"):
            attachments.append({
                "type": "image",
                "url": raw_request["image_url"]
            })
        
        # Handle multiple images
        if raw_request.get("images"):
            for img in raw_request["images"]:
                if isinstance(img, str):
                    attachments.append({"type": "image", "url": img})
                elif isinstance(img, dict):
                    attachments.append(img)
        
        return attachments
    
    def get_conversation_history(
        self,
        conversation_id: str,
        limit: int = 10
    ) -> List[Dict[str, str]]:
        """Retrieve conversation history from Redis.
        
        Args:
            conversation_id: Conversation identifier
            limit: Maximum messages to retrieve
            
        Returns:
            List of conversation messages
        """
        # This would integrate with Redis to fetch history
        # For now, return empty list
        return []
    
    async def health_check(self) -> bool:
        """Check adapter health.
        
        Returns:
            True if healthy
        """
        return True


class StreamingWebAdapter(WebAdapter):
    """Extended Web adapter supporting streaming responses.
    
    Used for real-time chat experiences with Server-Sent Events.
    """
    
    async def format_stream(
        self,
        response: AdapterResponse,
        chunk_callback: callable
    ) -> None:
        """Format response as SSE stream.
        
        Args:
            response: Response to stream
            chunk_callback: Async callback for each chunk
        """
        # Stream the message in chunks
        message = response.message
        chunk_size = 20  # Characters per chunk
        
        for i in range(0, len(message), chunk_size):
            chunk = message[i:i + chunk_size]
            await chunk_callback({
                "type": "chunk",
                "content": chunk,
                "done": i + chunk_size >= len(message)
            })
        
        # Send final metadata
        await chunk_callback({
            "type": "done",
            "metadata": {
                "agent": response.agent_used,
                "cached": response.cached
            }
        })
