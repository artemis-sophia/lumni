"""
Redis Cache Layer
Wraps aiocache library to maintain existing API
"""

import json
from typing import Optional, Any
from urllib.parse import urlparse
from aiocache import Cache as AiocacheCache
from aiocache.serializers import JsonSerializer
from app.utils.logger import Logger


class Cache:
    """Redis cache wrapper using aiocache"""

    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis_url = redis_url
        self.logger = Logger("Cache")
        self._connected = False
        
        # Parse Redis URL
        parsed = urlparse(redis_url)
        endpoint = parsed.hostname or "localhost"
        port = parsed.port or 6379
        db = int(parsed.path.lstrip('/')) if parsed.path and parsed.path != '/' else 0
        
        # Initialize aiocache with Redis backend and JSON serializer
        self._cache = AiocacheCache(
            AiocacheCache.REDIS,
            endpoint=endpoint,
            port=port,
            db=db,
            serializer=JsonSerializer()
        )

    async def connect(self):
        """Connect to Redis (aiocache connects automatically, this is for compatibility)"""
        try:
            # aiocache connects automatically on first operation
            # Test connection with a ping-like operation
            try:
                await self._cache.get("__connection_test__")
            except Exception:
                # If get fails, try set as connection test
                await self._cache.set("__connection_test__", "test", ttl=1)
            self._connected = True
            self.logger.info("Connected to Redis")
        except Exception as e:
            self.logger.error(f"Failed to connect to Redis: {str(e)}")
            self._connected = False

    async def disconnect(self):
        """Disconnect from Redis"""
        try:
            # aiocache has close method
            await self._cache.close()
            self._connected = False
        except Exception as e:
            self.logger.warn(f"Error disconnecting from Redis: {str(e)}")
            self._connected = False

    async def get(self, key: str) -> Optional[str]:
        """Get value from cache"""
        try:
            value = await self._cache.get(key)
            if value is None:
                return None
            # aiocache with JsonSerializer returns deserialized value
            # Convert back to string if needed for compatibility
            if not isinstance(value, str):
                return json.dumps(value)
            return value
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
        try:
            # Try to parse as JSON, if fails use as string
            try:
                parsed_value = json.loads(value)
            except (json.JSONDecodeError, TypeError):
                parsed_value = value
            
            await self._cache.set(key, parsed_value, ttl=ttl)
        except Exception as e:
            self.logger.warn(f"Cache set failed for key {key}: {str(e)}")

    async def get_json(self, key: str) -> Optional[Any]:
        """Get JSON value from cache"""
        try:
            # aiocache with JsonSerializer already deserializes
            value = await self._cache.get(key)
            return value
        except Exception as e:
            self.logger.warn(f"Cache get_json failed for key {key}: {str(e)}")
            return None

    async def set_json(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ):
        """Set JSON value in cache"""
        try:
            await self._cache.set(key, value, ttl=ttl)
        except Exception as e:
            self.logger.warn(f"Failed to set JSON value for key {key}: {str(e)}")

    async def delete(self, key: str):
        """Delete key from cache"""
        try:
            await self._cache.delete(key)
        except Exception as e:
            self.logger.warn(f"Cache delete failed for key {key}: {str(e)}")

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            value = await self._cache.get(key)
            return value is not None
        except Exception as e:
            self.logger.warn(f"Cache exists check failed for key {key}: {str(e)}")
            return False

    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment a counter in cache"""
        try:
            # aiocache has increment method
            return await self._cache.increment(key, delta=amount)
        except Exception as e:
            self.logger.warn(f"Cache increment failed for key {key}: {str(e)}")
            return None

    async def expire(self, key: str, seconds: int):
        """Set expiration on key"""
        try:
            # Get current value and set with new TTL
            value = await self._cache.get(key)
            if value is not None:
                await self._cache.set(key, value, ttl=seconds)
        except Exception as e:
            self.logger.warn(f"Cache expire failed for key {key}: {str(e)}")
