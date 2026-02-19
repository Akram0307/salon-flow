"""Redis client for caching"""
import redis.asyncio as redis
import structlog
from typing import Optional, Any
import json

logger = structlog.get_logger()


class RedisClient:
    """Async Redis client wrapper"""
    
    def __init__(self, url: str = "redis://localhost:6379"):
        self.url = url
        self.client: Optional[redis.Redis] = None
    
    async def connect(self):
        """Connect to Redis"""
        self.client = redis.from_url(self.url, encoding="utf-8", decode_responses=True)
        await self.client.ping()
        logger.info("Connected to Redis", url=self.url)
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.client:
            await self.client.close()
            logger.info("Disconnected from Redis")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis"""
        if not self.client:
            return None
        value = await self.client.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None
    
    async def set(self, key: str, value: Any, expire: int = 3600):
        """Set value in Redis with expiration"""
        if not self.client:
            return
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        await self.client.set(key, value, ex=expire)
    
    async def delete(self, key: str):
        """Delete key from Redis"""
        if self.client:
            await self.client.delete(key)
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        if not self.client:
            return False
        return await self.client.exists(key) > 0


redis_client = RedisClient()
