"""Redis Cache Service for AI Responses

Caches AI responses to reduce API calls and improve latency.
"""
import json
import hashlib
from typing import Optional, Any, Dict
import redis.asyncio as redis
import structlog

from app.core.config import get_settings

logger = structlog.get_logger()
settings = get_settings()


class CacheService:
    """Redis-based cache for AI responses"""
    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or settings.redis_url
        self._client: Optional[redis.Redis] = None
        self._enabled = settings.enable_cache
        
    async def _ensure_client(self):
        """Ensure Redis client is initialized"""
        if self._client is None:
            self._client = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
    
    async def close(self):
        """Close Redis connection"""
        if self._client:
            await self._client.close()
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
            value = await self._client.get(key)
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
            await self._client.setex(
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
            keys = []
            async for key in self._client.scan_iter(match=f"ai:{pattern}:*"):
                keys.append(key)
            
            if keys:
                deleted = await self._client.delete(*keys)
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
