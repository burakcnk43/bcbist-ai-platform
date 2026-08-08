import diskcache
import os
from backend.core.config import settings
from backend.core.logger import logger

# Ensure cache directory exists
os.makedirs(settings.CACHE_DIR, exist_ok=True)

cache = diskcache.Cache(settings.CACHE_DIR)

def get_cached(key: str):
    """Retrieve data from cache with logging."""
    value = cache.get(key)
    if value:
        logger.info(f"[CACHE HIT] {key}")
    else:
        logger.info(f"[CACHE MISS] {key}")
    return value

def set_cached(key: str, value, expire: int = settings.CACHE_TIME):
    """Store data in cache."""
    cache.set(key, value, expire=expire)
