"""
Redis Cache Layer
Provides caching for model lists, rate limits, and responses
"""

import json
from typing import Optional, Any, TypeVar
from datetime import timedelta
import redis.asyncio as aioredis
from app.utils.logger import Logger

T = TypeVar('T')


class Cache:
    """Redis cache wrapper"""

    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis_url = redis_url
        self.client: Optional[aioredis.Redis] = None
        self.logger = Logger("Cache")
        self._connected = False

    async def connect(self):
        """Connect to Redis"""
        try:
            self.client = await aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await self.client.ping()
            self._connected = True
            self.logger.info("Connected to Redis")
        except Exception as e:
            self.logger.error(f"Failed to connect to Redis: {str(e)}")
            self._connected = False

    async def disconnect(self):
        """Disconnect from Redis"""
        if self.client:
            await self.client.close()
            self._connected = False

    async def get(self, key: str) -> Optional[str]:
        """Get value from cache"""
        if not self._connected or not self.client:
            return None
        
        try:
            return await self.client.get(key)
        except Exception as e:
            self.logger.warn(f"Cache get failed for key {key}: {str(e)}")
            return None

    async def set(
        self,
        key: str,
        value: str,
        ttl: Optional[int] = None
    ):
        """Set value in cache with optional TTL"""
        if not self._connected or not self.client:
            return
        
        try:
            if ttl:
                await self.client.setex(key, ttl, value)
            else:
                await self.client.set(key, value)
        except Exception as e:
            self.logger.warn(f"Cache set failed for key {key}: {str(e)}")

    async def get_json(self, key: str) -> Optional[Any]:
        """Get JSON value from cache"""
        value = await self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return None
        return None

    async def set_json(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ):
        """Set JSON value in cache"""
        try:
            json_value = json.dumps(value)
            await self.set(key, json_value, ttl)
        except (TypeError, ValueError) as e:
            self.logger.warn(f"Failed to serialize value for key {key}: {str(e)}")

    async def delete(self, key: str):
        """Delete key from cache"""
        if not self._connected or not self.client:
            return
        
        try:
            await self.client.delete(key)
        except Exception as e:
            self.logger.warn(f"Cache delete failed for key {key}: {str(e)}")

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        if not self._connected or not self.client:
            return False
        
        try:
            return bool(await self.client.exists(key))
        except Exception as e:
            self.logger.warn(f"Cache exists check failed for key {key}: {str(e)}")
            return False

    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment a counter in cache"""
        if not self._connected or not self.client:
            return None
        
        try:
            return await self.client.incrby(key, amount)
        except Exception as e:
            self.logger.warn(f"Cache increment failed for key {key}: {str(e)}")
            return None

    async def expire(self, key: str, seconds: int):
        """Set expiration on key"""
        if not self._connected or not self.client:
            return
        
        try:
            await self.client.expire(key, seconds)
        except Exception as e:
            self.logger.warn(f"Cache expire failed for key {key}: {str(e)}")

