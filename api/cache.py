"""
BALE Caching Layer
Redis-based caching for analysis results and API responses.
"""
import os
import json
import hashlib
from typing import Optional, Any, Union
from datetime import timedelta
from functools import wraps
from src.logger import setup_logger
logger = setup_logger("bale_cache")
# ==================== REDIS CLIENT ====================
class RedisCache:
"""
Redis caching layer with serialization and expiry support.
"""
def __init__(self, url: str = None):
self.url = url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
self._client = None
self._connected = False
def connect(self) -> bool:
"""Establish connection to Redis."""
try:
import redis
self._client = redis.from_url(
self.url,
encoding="utf-8",
decode_responses=True
)
self._client.ping()
self._connected = True
logger.info(f"Connected to Redis at {self.url}")
return True
except ImportError:
logger.warning("redis package not installed")
return False
except Exception as e:
logger.warning(f"Redis connection failed: {e}")
return False
@property
def is_connected(self) -> bool:
return self._connected
def _serialize(self, value: Any) -> str:
"""Serialize a value to string."""
return json.dumps(value, default=str)
def _deserialize(self, value: str) -> Any:
"""Deserialize a string to value."""
if value is None:
return None
try:
return json.loads(value)
except:
return value
def get(self, key: str) -> Optional[Any]:
"""Get a value from cache."""
if not self._connected:
return None
try:
value = self._client.get(key)
return self._deserialize(value)
except Exception as e:
logger.warning(f"Cache get error: {e}")
return None
def set(
self, key: str, value: Any, ttl: Union[int, timedelta] = 3600
) -> bool:
"""
Set a value in cache with optional TTL.
Args:
key: Cache key
value: Value to cache (will be JSON serialized)
ttl: Time to live in seconds or timedelta
"""
if not self._connected:
return False
try:
if isinstance(ttl, timedelta):
ttl = int(ttl.total_seconds())
self._client.setex(key, ttl, self._serialize(value))
return True
except Exception as e:
logger.warning(f"Cache set error: {e}")
return False
def delete(self, key: str) -> bool:
"""Delete a key from cache."""
if not self._connected:
return False
try:
self._client.delete(key)
return True
except Exception as e:
logger.warning(f"Cache delete error: {e}")
return False
def exists(self, key: str) -> bool:
"""Check if a key exists."""
if not self._connected:
return False
try:
return self._client.exists(key) > 0
except:
return False
def clear_pattern(self, pattern: str) -> int:
"""Delete all keys matching a pattern."""
if not self._connected:
return 0
try:
keys = self._client.keys(pattern)
if keys:
return self._client.delete(*keys)
return 0
except Exception as e:
logger.warning(f"Cache clear error: {e}")
return 0
def incr(self, key: str, amount: int = 1) -> Optional[int]:
"""Increment a counter."""
if not self._connected:
return None
try:
return self._client.incrby(key, amount)
except:
return None
# ==================== CACHE KEY GENERATION ====================
def make_cache_key(prefix: str, *args, **kwargs) -> str:
"""Generate a deterministic cache key."""
key_parts = [prefix]
for arg in args:
if arg is not None:
key_parts.append(str(arg))
for k, v in sorted(kwargs.items()):
if v is not None:
key_parts.append(f"{k}:{v}")
key_string = ":".join(key_parts)
# Hash long keys
if len(key_string) > 100:
key_hash = hashlib.md5(key_string.encode()).hexdigest()[:16]
return f"{prefix}:{key_hash}"
return key_string
def analysis_cache_key(clause_text: str, jurisdiction: str, depth: str) -> str:
"""Generate cache key for analysis results."""
content_hash = hashlib.md5(clause_text.encode()).hexdigest()[:12]
return f"analysis:{jurisdiction}:{depth}:{content_hash}"
# ==================== DECORATORS ====================
def cached(
prefix: str,
ttl: int = 3600,
key_builder: callable = None
):
"""
Decorator for caching function results.
Usage:
@cached("my_func", ttl=300)
async def my_func(arg1, arg2):
...
"""
def decorator(func):
@wraps(func)
async def wrapper(*args, **kwargs):
# Skip cache if not connected
if not cache.is_connected:
return await func(*args, **kwargs)
# Build cache key
if key_builder:
key = key_builder(*args, **kwargs)
else:
key = make_cache_key(prefix, *args, **kwargs)
# Try cache
cached_value = cache.get(key)
if cached_value is not None:
logger.debug(f"Cache hit: {key}")
return cached_value
# Execute function
result = await func(*args, **kwargs)
# Store in cache
cache.set(key, result, ttl)
logger.debug(f"Cache set: {key}")
return result
return wrapper
return decorator
def cache_invalidate(pattern: str):
"""
Decorator to invalidate cache after function execution.
Usage:
@cache_invalidate("contracts:*")
async def update_contract(...):
...
"""
def decorator(func):
@wraps(func)
async def wrapper(*args, **kwargs):
result = await func(*args, **kwargs)
if cache.is_connected:
count = cache.clear_pattern(pattern)
logger.debug(f"Cache invalidated: {pattern} ({count} keys)")
return result
return wrapper
return decorator
# ==================== MEMOIZATION ====================
class AnalysisMemo:
"""
Memoization for expensive analysis operations.
Stores results in Redis with configurable TTL.
"""
def __init__(self, redis_cache: RedisCache):
self.cache = redis_cache
self.default_ttl = timedelta(hours=24)
def get_or_compute(
self,
key: str,
compute_fn: callable,
ttl: timedelta = None
) -> Any:
"""
Get cached result or compute and cache.
Args:
key: Cache key
compute_fn: Function to call if not cached (sync)
ttl: Time to live
"""
cached = self.cache.get(key)
if cached is not None:
return cached
result = compute_fn()
self.cache.set(key, result, ttl or self.default_ttl)
return result
async def get_or_compute_async(
self,
key: str,
compute_fn: callable,
ttl: timedelta = None
) -> Any:
"""Async version of get_or_compute."""
cached = self.cache.get(key)
if cached is not None:
return cached
result = await compute_fn()
self.cache.set(key, result, ttl or self.default_ttl)
return result
def invalidate(self, key: str):
"""Invalidate a specific key."""
self.cache.delete(key)
def invalidate_user(self, user_id: str):
"""Invalidate all cached analyses for a user."""
self.cache.clear_pattern(f"analysis:{user_id}:*")
# ==================== RESPONSE CACHE MIDDLEWARE ====================
class CacheMiddleware:
"""
FastAPI middleware for response caching.
"""
def __init__(
self,
redis_cache: RedisCache,
ttl: int = 60,
cache_methods: list = ["GET"],
exclude_paths: list = None
):
self.cache = redis_cache
self.ttl = ttl
self.cache_methods = cache_methods
self.exclude_paths = exclude_paths or ["/health", "/docs", "/openapi.json"]
def should_cache(self, request) -> bool:
"""Determine if request should be cached."""
if request.method not in self.cache_methods:
return False
if any(request.url.path.startswith(p) for p in self.exclude_paths):
return False
return True
def cache_key_from_request(self, request) -> str:
"""Generate cache key from request."""
path = request.url.path
query = str(sorted(request.query_params.items()))
key_hash = hashlib.md5(f"{path}:{query}".encode()).hexdigest()[:16]
return f"response:{key_hash}"
# ==================== GLOBAL INSTANCE ====================
cache = RedisCache()
def init_cache() -> bool:
"""Initialize the global cache connection."""
return cache.connect()
def get_cache() -> RedisCache:
"""Get the global cache instance."""
return cache
# Analysis memo using global cache
analysis_memo = AnalysisMemo(cache)
