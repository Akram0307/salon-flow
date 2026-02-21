"""Redis Cache Service for AI Responses

Caches AI responses to reduce API calls and improve latency.
Uses Upstash Redis REST API for serverless compatibility.
"""
import json
import hashlib
from typing import Optional, Any, Dict
from upstash_redis import Redis
import structlog

from app.core.config import get_settings

logger = structlog.get_logger()
settings = get_settings()


class CacheService:
    """Upstash Redis-based cache for AI responses"""
    
    def __init__(
        self,
        upstash_url: Optional[str] = None,
        upstash_token: Optional[str] = None
    ):
        self.upstash_url = upstash_url or settings.upstash_redis_rest_url
        self.upstash_token = upstash_token or settings.upstash_redis_rest_token
        self._client: Optional[Redis] = None
        self._enabled = settings.enable_cache and bool(self.upstash_url and self.upstash_token)
        
    async def _ensure_client(self):
        """Ensure Redis client is initialized"""
        if self._client is None and self._enabled:
            self._client = Redis(
                url=self.upstash_url,
                token=self.upstash_token,
            )
    
    async def close(self):
        """Close Redis connection (no-op for REST client)"""
        # Upstash REST client doesn't maintain persistent connections
        self._client = None
    
    def _generate_key(self, prefix: str, data: Any) -> str:
        """Generate cache key from data"""
        data_str = json.dumps(data, sort_keys=True)
        hash_val = hashlib.sha256(data_str.encode()).hexdigest()[:16]
        return f"ai:{prefix}:{hash_val}"
    
    async def get(self, key: str) -> Optional[str]:
        """Get cached value"""
        if not self._enabled:
            return None
            
        try:
            await self._ensure_client()
            value = self._client.get(key)
            if value:
                logger.info("cache_hit", key=key)
            return value
        except Exception as e:
            logger.warning("cache_get_error", error=str(e))
            return None
    
    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        """Set cached value"""
        if not self._enabled:
            return False
            
        try:
            await self._ensure_client()
            self._client.setex(
                key,
                ttl or settings.cache_ttl,
                value
            )
            logger.info("cache_set", key=key, ttl=ttl or settings.cache_ttl)
            return True
        except Exception as e:
            logger.warning("cache_set_error", error=str(e))
            return False
    
    async def get_or_compute(
        self,
        prefix: str,
        data: Dict[str, Any],
        compute_fn,
        ttl: Optional[int] = None
    ) -> str:
        """Get from cache or compute and cache result"""
        key = self._generate_key(prefix, data)
        
        cached = await self.get(key)
        if cached:
            return cached
        
        result = await compute_fn()
        
        if result:
            await self.set(key, result, ttl)
        
        return result
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching pattern"""
        try:
            await self._ensure_client()
            # Use SCAN to find matching keys
            keys = []
            cursor = 0
            while True:
                result = self._client.scan(cursor, match=f"ai:{pattern}:*")
                cursor = result[0]
                keys.extend(result[1])
                if cursor == 0:
                    break
            
            if keys:
                deleted = self._client.delete(*keys)
                logger.info("cache_invalidated", pattern=pattern, count=deleted)
                return deleted
            return 0
        except Exception as e:
            logger.warning("cache_invalidate_error", error=str(e))
            return 0


# Singleton instance
_cache_instance: Optional[CacheService] = None


async def get_cache_service() -> CacheService:
    """Get or create cache service singleton"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = CacheService()
        await _cache_instance._ensure_client()
    return _cache_instance
