"""
Redis Cache Service
Handles caching for papers, summaries, and API responses
"""

import json
import logging
from datetime import timedelta
from typing import Any, Optional

import redis
from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class CacheService:
    """Redis cache service for application data"""

    def __init__(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )
            # Test connection
            self.redis_client.ping()
            logger.info("Redis cache service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None

    def _get_key(self, prefix: str, identifier: str) -> str:
        """Generate cache key with prefix"""
        return f"{settings.APP_NAME}:{prefix}:{identifier}"

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        if not self.redis_client:
            return None

        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None

    def set(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None,
    ) -> bool:
        """
        Set value in cache

        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            expire: Expiration time in seconds (default from settings)

        Returns:
            True if successful, False otherwise
        """
        if not self.redis_client:
            return False

        try:
            expire = expire or settings.CACHE_TTL
            serialized = json.dumps(value, default=str)
            self.redis_client.setex(key, expire, serialized)
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.redis_client:
            return False

        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False

    def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern

        Args:
            pattern: Key pattern (e.g., "papers:*")

        Returns:
            Number of keys deleted
        """
        if not self.redis_client:
            return 0

        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache delete pattern error for {pattern}: {e}")
            return 0

    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        if not self.redis_client:
            return False

        try:
            return self.redis_client.exists(key) > 0
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}")
            return False

    # Paper-specific cache methods
    def get_paper(self, paper_id: str) -> Optional[dict]:
        """Get cached paper by ID"""
        key = self._get_key("paper", paper_id)
        return self.get(key)

    def set_paper(self, paper_id: str, paper_data: dict, expire: int = 3600) -> bool:
        """Cache paper data"""
        key = self._get_key("paper", paper_id)
        return self.set(key, paper_data, expire)

    def get_paper_summary(self, paper_id: str) -> Optional[dict]:
        """Get cached paper summary"""
        key = self._get_key("summary", paper_id)
        return self.get(key)

    def set_paper_summary(
        self, paper_id: str, summary_data: dict, expire: int = 7200
    ) -> bool:
        """Cache paper summary (longer TTL since summaries are expensive to generate)"""
        key = self._get_key("summary", paper_id)
        return self.set(key, summary_data, expire)

    def get_random_papers(
        self, count: int, field: Optional[str] = None
    ) -> Optional[list]:
        """Get cached random papers"""
        field_key = field or "all"
        key = self._get_key("random", f"{field_key}:{count}")
        return self.get(key)

    def set_random_papers(
        self, count: int, papers: list, field: Optional[str] = None, expire: int = 300
    ) -> bool:
        """Cache random papers (short TTL for freshness)"""
        field_key = field or "all"
        key = self._get_key("random", f"{field_key}:{count}")
        return self.set(key, papers, expire)

    def get_search_results(self, query: str, filters: str = "") -> Optional[dict]:
        """Get cached search results"""
        cache_key = f"{query}:{filters}"
        key = self._get_key("search", cache_key)
        return self.get(key)

    def set_search_results(
        self, query: str, results: dict, filters: str = "", expire: int = 600
    ) -> bool:
        """Cache search results"""
        cache_key = f"{query}:{filters}"
        key = self._get_key("search", cache_key)
        return self.set(key, results, expire)

    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment counter"""
        if not self.redis_client:
            return None

        try:
            return self.redis_client.incr(key, amount)
        except Exception as e:
            logger.error(f"Cache increment error for key {key}: {e}")
            return None

    def get_stats(self) -> dict:
        """Get cache statistics"""
        if not self.redis_client:
            return {"status": "unavailable"}

        try:
            info = self.redis_client.info()
            return {
                "status": "connected",
                "used_memory": info.get("used_memory_human", "N/A"),
                "connected_clients": info.get("connected_clients", 0),
                "total_keys": self.redis_client.dbsize(),
                "hit_rate": info.get("keyspace_hits", 0)
                / (info.get("keyspace_hits", 0) + info.get("keyspace_misses", 1)),
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"status": "error", "error": str(e)}

    def clear_all(self) -> bool:
        """Clear all cache (use with caution!)"""
        if not self.redis_client:
            return False

        try:
            self.redis_client.flushdb()
            logger.warning("Cache cleared completely")
            return True
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False

    def set_with_lock(
        self, key: str, value: Any, lock_timeout: int = 10, expire: int = None
    ) -> bool:
        """
        Set value with distributed lock to prevent race conditions

        Args:
            key: Cache key
            value: Value to cache
            lock_timeout: Lock timeout in seconds
            expire: Cache expiration

        Returns:
            True if successful
        """
        if not self.redis_client:
            return False

        lock_key = f"lock:{key}"
        try:
            # Try to acquire lock
            lock = self.redis_client.set(lock_key, "1", nx=True, ex=lock_timeout)
            if not lock:
                logger.warning(f"Could not acquire lock for key {key}")
                return False

            # Set the value
            result = self.set(key, value, expire)

            # Release lock
            self.redis_client.delete(lock_key)
            return result

        except Exception as e:
            logger.error(f"Error in set_with_lock for key {key}: {e}")
            # Try to release lock on error
            try:
                self.redis_client.delete(lock_key)
            except:
                pass
            return False


# Global cache service instance
_cache_service = None


def get_cache_service() -> CacheService:
    """Get or create cache service singleton"""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service
