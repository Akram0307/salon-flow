"""OpenRouter Client for AI Model Integration

Handles communication with OpenRouter API to access Gemini models.
Supports streaming, caching, and error handling.
"""
import httpx
import json
import hashlib
from typing import Optional, List, Dict, Any, AsyncIterator, Union
from pydantic import BaseModel, Field
import structlog

from app.core.config import get_settings

logger = structlog.get_logger()
settings = get_settings()


class ChatMessage(BaseModel):
    """Chat message structure"""
    role: str = Field(..., description="Message role: system, user, or assistant")
    content: str = Field(..., description="Message content")
    
    def to_dict(self) -> Dict[str, str]:
        return {"role": self.role, "content": self.content}


class OpenRouterResponse(BaseModel):
    """OpenRouter API response"""
    id: str
    model: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]
    
    @property
    def content(self) -> str:
        """Extract content from first choice"""
        if self.choices:
            return self.choices[0].get("message", {}).get("content", "")
        return ""


class OpenRouterClient:
    """Async client for OpenRouter API"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        default_model: Optional[str] = None,
    ):
        self.api_key = api_key or settings.openrouter_api_key
        self.base_url = base_url or settings.openrouter_base_url
        self.default_model = default_model or settings.default_model
        self._client: Optional[httpx.AsyncClient] = None
        
    async def __aenter__(self):
        await self._ensure_client()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
        
    async def _ensure_client(self):
        """Ensure HTTP client is initialized"""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(120.0, connect=30.0),
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": settings.openrouter_site_url,
                    "X-Title": settings.openrouter_site_name,
                }
            )
    
    async def close(self):
        """Close HTTP client"""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
    
    def _build_messages(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        history: Optional[List[ChatMessage]] = None,
    ) -> List[Dict[str, str]]:
        """Build message list for API call"""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        if history:
            messages.extend([msg.to_dict() for msg in history])
        
        messages.append({"role": "user", "content": prompt})
        return messages
    
    async def chat(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        history: Optional[List[ChatMessage]] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> OpenRouterResponse:
        """Send a chat completion request"""
        await self._ensure_client()
        
        messages = self._build_messages(prompt, system_prompt, history)
        
        payload = {
            "model": model or self.default_model,
            "messages": messages,
            "temperature": temperature or settings.temperature,
            "max_tokens": max_tokens or settings.max_tokens,
            **kwargs
        }
        
        logger.info(
            "openrouter_request",
            model=payload["model"],
            message_count=len(messages)
        )
        
        try:
            response = await self._client.post(
                f"{self.base_url}/chat/completions",
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            result = OpenRouterResponse(**data)
            
            logger.info(
                "openrouter_response",
                model=result.model,
                tokens_used=result.usage.get("total_tokens", 0)
            )
            
            return result
            
        except httpx.HTTPStatusError as e:
            logger.error(
                "openrouter_http_error",
                status_code=e.response.status_code,
                error=str(e)
            )
            # Try fallback model if available
            if model is None and settings.fallback_model != self.default_model:
                logger.warning("trying_fallback_model", model=settings.fallback_model)
                return await self.chat(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    history=history,
                    model=settings.fallback_model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )
            raise
            
        except Exception as e:
            logger.error("openrouter_error", error=str(e))
            raise
    
    async def chat_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        history: Optional[List[ChatMessage]] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream chat completion response"""
        await self._ensure_client()
        
        messages = self._build_messages(prompt, system_prompt, history)
        
        payload = {
            "model": model or self.default_model,
            "messages": messages,
            "temperature": temperature or settings.temperature,
            "max_tokens": max_tokens or settings.max_tokens,
            "stream": True,
            **kwargs
        }
        
        async with self._client.stream(
            "POST",
            f"{self.base_url}/chat/completions",
            json=payload
        ) as response:
            response.raise_for_status()
            
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                        if chunk.get("choices"):
                            delta = chunk["choices"][0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                yield content
                    except json.JSONDecodeError:
                        continue
    
    async def generate_with_context(
        self,
        prompt: str,
        context: Dict[str, Any],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> OpenRouterResponse:
        """Generate response with salon context injected"""
        # Build context-aware system prompt
        context_str = self._format_context(context)
        enhanced_system = f"""{system_prompt or 'You are a helpful AI assistant for salon management.'}

Current Salon Context:
{context_str}
"""
        
        return await self.chat(
            prompt=prompt,
            system_prompt=enhanced_system,
            **kwargs
        )
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context dictionary as readable string"""
        lines = []
        for key, value in context.items():
            if isinstance(value, dict):
                lines.append(f"{key}:")
                for k, v in value.items():
                    lines.append(f"  - {k}: {v}")
            elif isinstance(value, list):
                lines.append(f"{key}: {', '.join(str(v) for v in value[:5])}")
                if len(value) > 5:
                    lines.append(f"  ... and {len(value) - 5} more")
            else:
                lines.append(f"{key}: {value}")
        return "\n".join(lines)


# Singleton instance
_client_instance: Optional[OpenRouterClient] = None


async def get_openrouter_client() -> OpenRouterClient:
    """Get or create OpenRouter client singleton"""
    global _client_instance
    if _client_instance is None:
        _client_instance = OpenRouterClient()
        await _client_instance._ensure_client()
    return _client_instance
