"""
Utility functions for property-related operations with caching.
"""

from django.core.cache import cache
from .models import Property
import logging

# Set up logger for debugging cache operations
logger = logging.getLogger(__name__)

def get_all_properties():
    """
    Get all properties from cache or database.
    
    Returns:
        QuerySet: All Property objects, cached for 1 hour (3600 seconds)
    """
    cache_key = 'all_properties'
    
    # Try to get from cache first
    cached_data = cache.get(cache_key)
    
    if cached_data is not None:
        logger.info(f"Cache HIT for key: {cache_key}")
        return cached_data
    
    # Cache miss - fetch from database
    logger.info(f"Cache MISS for key: {cache_key}. Fetching from database...")
    properties = Property.objects.all().order_by('-created_at')
    
    # Store in cache for 1 hour (3600 seconds)
    cache.set(cache_key, properties, 3600)
    logger.info(f"Cached {properties.count()} properties for 3600 seconds")
    
    return properties


def clear_properties_cache():
    """
    Clear the cached properties.
    Useful when properties are added, updated, or deleted.
    """
    cache_key = 'all_properties'
    deleted = cache.delete(cache_key)
    
    if deleted:
        logger.info(f"Cache cleared for key: {cache_key}")
        return True
    logger.info(f"No cache found for key: {cache_key}")
    return False


def get_property_count():
    """
    Get the count of properties with caching.
    """
    cache_key = 'property_count'
    cached_count = cache.get(cache_key)
    
    if cached_count is not None:
        return cached_count
    
    count = Property.objects.count()
    # Cache count for 30 minutes (1800 seconds)
    cache.set(cache_key, count, 1800)
    return count