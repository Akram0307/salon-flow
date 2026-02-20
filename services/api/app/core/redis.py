"""Enhanced Redis client for caching with connection pooling and utilities.

Supports both local Redis and Upstash (serverless Redis with TLS).
"""
import os
import redis.asyncio as redis
from redis.asyncio.connection import ConnectionPool
import structlog
from typing import Optional, Any, List, Callable, TypeVar, ParamSpec
from functools import wraps
import json
import hashlib
import gzip
import base64
import asyncio
from datetime import timedelta

logger = structlog.get_logger()

P = ParamSpec('P')
T = TypeVar('T')


class CacheConfig:
    """Cache configuration constants."""
    # Default TTLs for different data types (in seconds)
    SALON_CONFIG_TTL = 3600  # 1 hour - salon configs change rarely
    SERVICE_CATALOG_TTL = 1800  # 30 minutes - services change occasionally
    STAFF_LIST_TTL = 600  # 10 minutes - staff availability changes
    CUSTOMER_TTL = 300  # 5 minutes - customer data changes frequently
    BOOKING_TTL = 60  # 1 minute - booking data changes rapidly

    # Cache key prefixes
    PREFIX_SALON = "salon"
    PREFIX_SERVICE = "service"
    PREFIX_STAFF = "staff"
    PREFIX_CUSTOMER = "customer"
    PREFIX_BOOKING = "booking"
    PREFIX_CATALOG = "catalog"


class RedisClient:
    """Enhanced async Redis client with connection pooling and caching utilities.
    
    Supports:
    - Local Redis (redis://)
    - Upstash Redis (rediss://) with TLS
    - Connection pooling for optimal performance
    - Graceful fallback when Redis is unavailable
    """

    def __init__(self, url: str = None):
        # Support both REDIS_URL and UPSTASH_REDIS_URL env vars
        self.url = url or os.getenv("UPSTASH_REDIS_URL") or os.getenv("REDIS_URL", "redis://localhost:6379")
        self._pool: Optional[ConnectionPool] = None
        self.client: Optional[redis.Redis] = None
        self._connected = False
        self._is_upstash = self.url.startswith("rediss://")

        # Connection pool settings for optimal performance
        self.pool_settings = {
            "max_connections": 50,
            "retry_on_timeout": True,
            "health_check_interval": 30,
            "socket_keepalive": True,
            "socket_connect_timeout": 5,
            "socket_timeout": 5,
        }
        
        # Upstash-specific settings
        if self._is_upstash:
            # Upstash requires TLS and has different connection settings
            self.pool_settings["ssl_cert_reqs"] = None  # Allow self-signed certs
            logger.info("Configured for Upstash Redis with TLS")

    async def connect(self):
        """Connect to Redis with connection pooling."""
        if self._connected and self.client:
            return

        try:
            self._pool = ConnectionPool.from_url(
                self.url,
                encoding="utf-8",
                decode_responses=True,
                **self.pool_settings
            )
            self.client = redis.Redis(connection_pool=self._pool)
            await self.client.ping()
            self._connected = True
            logger.info("Connected to Redis with connection pool", 
                       url=self.url.replace(self.url.split('@')[-1], '***') if '@' in self.url else self.url,
                       is_upstash=self._is_upstash)
        except Exception as e:
            logger.warning("Redis connection failed - running without cache", error=str(e))
            self._connected = False
            # Don't raise - allow app to run without Redis

    async def disconnect(self):
        """Disconnect from Redis and release connections."""
        if self.client:
            await self.client.aclose()
        if self._pool:
            await self._pool.aclose()
        self._connected = False
        logger.info("Disconnected from Redis")

    async def health_check(self) -> bool:
        """Check Redis connection health."""
        if not self.client:
            return False
        try:
            await self.client.ping()
            return True
        except Exception:
            return False

    @property
    def is_connected(self) -> bool:
        """Check if Redis is connected."""
        return self._connected and self.client is not None

    # ========================================================================
    # Basic Operations
    # ========================================================================

    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis with JSON deserialization."""
        if not self.is_connected:
            return None
        try:
            value = await self.client.get(key)
            if value:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            return None
        except Exception as e:
            logger.warning("Redis get failed", key=key, error=str(e))
            return None

    async def set(
        self,
        key: str,
        value: Any,
        expire: int = 3600,
        compress: bool = False,
        nx: bool = False
    ) -> bool:
        """Set value in Redis with optional compression."""
        if not self.is_connected:
            return False
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)

            if compress and len(value) > 1024:
                value = self._compress(value)
                await self.client.set(f"{key}:compressed", "1", ex=expire)

            if nx:
                return await self.client.set(key, value, ex=expire, nx=True)
            else:
                await self.client.set(key, value, ex=expire)
            return True
        except Exception as e:
            logger.warning("Redis set failed", key=key, error=str(e))
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from Redis."""
        if not self.is_connected:
            return False
        try:
            await self.client.delete(key, f"{key}:compressed")
            return True
        except Exception as e:
            logger.warning("Redis delete failed", key=key, error=str(e))
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        if not self.is_connected:
            return False
        try:
            return await self.client.exists(key) > 0
        except Exception:
            return False

    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration on a key."""
        if not self.is_connected:
            return False
        try:
            return await self.client.expire(key, seconds)
        except Exception:
            return False

    async def ttl(self, key: str) -> int:
        """Get remaining TTL for a key."""
        if not self.is_connected:
            return -2
        try:
            return await self.client.ttl(key)
        except Exception:
            return -2

    # ========================================================================
    # Batch Operations
    # ========================================================================

    async def get_multi(self, keys: List[str]) -> dict:
        """Get multiple values at once (pipeline)."""
        if not self.is_connected or not keys:
            return {}
        try:
            values = await self.client.mget(keys)
            result = {}
            for key, value in zip(keys, values):
                if value:
                    try:
                        result[key] = json.loads(value)
                    except json.JSONDecodeError:
                        result[key] = value
            return result
        except Exception as e:
            logger.warning("Redis mget failed", error=str(e))
            return {}

    async def set_multi(self, mapping: dict, expire: int = 3600) -> bool:
        """Set multiple values at once (pipeline)."""
        if not self.is_connected or not mapping:
            return False
        try:
            async with self.client.pipeline() as pipe:
                for key, value in mapping.items():
                    if isinstance(value, (dict, list)):
                        value = json.dumps(value)
                    pipe.set(key, value, ex=expire)
                await pipe.execute()
            return True
        except Exception as e:
            logger.warning("Redis mset failed", error=str(e))
            return False

    async def delete_multi(self, keys: List[str]) -> int:
        """Delete multiple keys at once."""
        if not self.is_connected or not keys:
            return 0
        try:
            all_keys = keys + [f"{k}:compressed" for k in keys]
            return await self.client.delete(*all_keys)
        except Exception as e:
            logger.warning("Redis multi-delete failed", error=str(e))
            return 0

    # ========================================================================
    # Pattern Operations
    # ========================================================================

    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching a pattern."""
        if not self.is_connected:
            return 0
        try:
            keys = []
            async for key in self.client.scan_iter(match=pattern):
                keys.append(key)
            if keys:
                return await self.client.delete(*keys)
            return 0
        except Exception as e:
            logger.warning("Redis pattern delete failed", pattern=pattern, error=str(e))
            return 0

    async def get_keys(self, pattern: str) -> List[str]:
        """Get all keys matching a pattern."""
        if not self.is_connected:
            return []
        try:
            keys = []
            async for key in self.client.scan_iter(match=pattern):
                keys.append(key)
            return keys
        except Exception:
            return []

    # ========================================================================
    # Cache Invalidation
    # ========================================================================

    async def invalidate_salon_cache(self, salon_id: str):
        """Invalidate all cache entries for a salon."""
        patterns = [
            f"{CacheConfig.PREFIX_SALON}:{salon_id}:*",
            f"{CacheConfig.PREFIX_SERVICE}:{salon_id}:*",
            f"{CacheConfig.PREFIX_STAFF}:{salon_id}:*",
            f"{CacheConfig.PREFIX_CATALOG}:{salon_id}:*",
        ]
        total_deleted = 0
        for pattern in patterns:
            total_deleted += await self.delete_pattern(pattern)
        logger.info("Invalidated salon cache", salon_id=salon_id, keys_deleted=total_deleted)
        return total_deleted

    async def invalidate_service_cache(self, salon_id: str, service_id: str = None):
        """Invalidate service cache entries."""
        if service_id:
            await self.delete(f"{CacheConfig.PREFIX_SERVICE}:{salon_id}:{service_id}")
        await self.delete_pattern(f"{CacheConfig.PREFIX_CATALOG}:{salon_id}:*")

    # ========================================================================
    # Utility Methods
    # ========================================================================

    @staticmethod
    def _compress(data: str) -> str:
        """Compress data using gzip and base64 encode."""
        compressed = gzip.compress(data.encode('utf-8'))
        return base64.b64encode(compressed).decode('utf-8')

    @staticmethod
    def _decompress(data: str) -> str:
        """Decompress gzip data."""
        compressed = base64.b64decode(data.encode('utf-8'))
        return gzip.decompress(compressed).decode('utf-8')

    @staticmethod
    def generate_cache_key(*parts: str) -> str:
        """Generate a cache key from parts."""
        return ":".join(str(p) for p in parts)

    @staticmethod
    def hash_key(data: Any) -> str:
        """Generate a hash key from data."""
        if isinstance(data, (dict, list)):
            data = json.dumps(data, sort_keys=True)
        return hashlib.md5(str(data).encode()).hexdigest()


# ============================================================================
# Cache Decorators
# ============================================================================

def cached(
    key_prefix: str,
    ttl: int = 3600,
    key_builder: Optional[Callable] = None,
    skip_cache: Optional[Callable] = None,
):
    """Decorator to cache function results."""
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            redis_client = kwargs.get('redis_client') or globals().get('redis_client')

            if not redis_client or not redis_client.is_connected:
                return await func(*args, **kwargs)

            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                key_parts = [key_prefix]
                for arg in args[1:]:
                    key_parts.append(str(arg))
                for k, v in sorted(kwargs.items()):
                    if k != 'redis_client':
                        key_parts.append(f"{k}={v}")
                cache_key = RedisClient.generate_cache_key(*key_parts)

            if skip_cache and skip_cache(*args, **kwargs):
                return await func(*args, **kwargs)

            cached_result = await redis_client.get(cache_key)
            if cached_result is not None:
                logger.debug("Cache hit", key=cache_key)
                return cached_result

            result = await func(*args, **kwargs)
            if result is not None:
                await redis_client.set(cache_key, result, expire=ttl)
                logger.debug("Cache set", key=cache_key, ttl=ttl)

            return result

        return wrapper
    return decorator


# Global instance
redis_client = RedisClient()
