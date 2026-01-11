"""
Redis cache metrics analysis functions.
"""

from django.core.cache import cache
from django_redis import get_redis_connection
import logging
import math

# Set up logger for cache metrics
logger = logging.getLogger(__name__)


def get_redis_cache_metrics():
    """
    Retrieve and analyze Redis cache hit/miss metrics.
    
    Returns:
        dict: Dictionary containing Redis cache metrics including:
            - hits: Number of cache hits
            - misses: Number of cache misses
            - hit_ratio: Cache hit ratio (0.0 to 1.0)
            - miss_ratio: Cache miss ratio (0.0 to 1.0)
            - total_operations: Total cache operations (hits + misses)
            - keyspace_hits: Raw keyspace_hits from Redis INFO
            - keyspace_misses: Raw keyspace_misses from Redis INFO
    """
    try:
        # Get Redis connection via django_redis
        redis_conn = get_redis_connection("default")
        
        # Get Redis INFO command output
        redis_info = redis_conn.info()
        
        # Extract cache statistics
        stats_section = redis_info.get('stats', {})
        
        # Get keyspace hits and misses
        keyspace_hits = stats_section.get('keyspace_hits', 0)
        keyspace_misses = stats_section.get('keyspace_misses', 0)
        
        # Calculate total requests/operations
        total_requests = keyspace_hits + keyspace_misses
        
        # Calculate hit ratio (hits / (hits + misses)) - FIXED LINE
        hit_ratio = keyspace_hits / total_requests if total_requests > 0 else 0
        
        # Calculate miss ratio
        miss_ratio = keyspace_misses / total_requests if total_requests > 0 else 0
        
        # Prepare metrics dictionary
        metrics = {
            'hits': keyspace_hits,
            'misses': keyspace_misses,
            'hit_ratio': hit_ratio,
            'hit_ratio_percentage': round(hit_ratio * 100, 2),
            'miss_ratio': miss_ratio,
            'miss_ratio_percentage': round(miss_ratio * 100, 2),
            'total_operations': total_requests,  # This is hits + misses
            'total_requests': total_requests,  # Alias for clarity
            'keyspace_hits': keyspace_hits,
            'keyspace_misses': keyspace_misses,
            'redis_version': redis_info.get('redis_version', 'unknown'),
            'connected_clients': redis_info.get('connected_clients', 0),
            'used_memory_human': redis_info.get('used_memory_human', '0B'),
            'uptime_in_seconds': redis_info.get('uptime_in_seconds', 0),
            'uptime_in_days': redis_info.get('uptime_in_days', 0),
        }
        
        # Log metrics
        logger.info(
            f"Redis Cache Metrics - "
            f"Hits: {keyspace_hits}, "
            f"Misses: {keyspace_misses}, "
            f"Hit Ratio: {hit_ratio:.2%}, "
            f"Total Requests: {total_requests}"
        )
        
        return metrics
        
    except Exception as e:
        logger.error(f"Error retrieving Redis cache metrics: {e}")
        
        # Return default metrics in case of error
        return {
            'hits': 0,
            'misses': 0,
            'hit_ratio': 0.0,
            'hit_ratio_percentage': 0.0,
            'miss_ratio': 0.0,
            'miss_ratio_percentage': 0.0,
            'total_operations': 0,
            'total_requests': 0,
            'keyspace_hits': 0,
            'keyspace_misses': 0,
            'error': str(e),
            'redis_version': 'unknown',
            'connected_clients': 0,
            'used_memory_human': '0B',
            'uptime_in_seconds': 0,
            'uptime_in_days': 0,
        }


# Alternative implementation with the exact formula requested
def get_cache_hit_ratio_simple():
    """
    Simple implementation that exactly matches the requirement:
    "Calculates hit ratio: hits / (hits + misses) if total_requests > 0 else 0"
    """
    try:
        redis_conn = get_redis_connection("default")
        redis_info = redis_conn.info()
        stats = redis_info.get('stats', {})
        
        hits = stats.get('keyspace_hits', 0)
        misses = stats.get('keyspace_misses', 0)
        total_requests = hits + misses
        
        # Exactly as specified in requirements
        hit_ratio = hits / total_requests if total_requests > 0 else 0
        
        return {
            'hits': hits,
            'misses': misses,
            'total_requests': total_requests,
            'hit_ratio': hit_ratio,
        }
    except Exception as e:
        logger.error(f"Error in get_cache_hit_ratio_simple: {e}")
        return {
            'hits': 0,
            'misses': 0,
            'total_requests': 0,
            'hit_ratio': 0,
            'error': str(e),
        }


# Update the get_redis_cache_metrics to use the exact formula
def get_redis_cache_metrics_exact():
    """
    Exact implementation matching the requirement specification.
    """
    try:
        redis_conn = get_redis_connection("default")
        redis_info = redis_conn.info()
        stats = redis_info.get('stats', {})
        
        hits = stats.get('keyspace_hits', 0)
        misses = stats.get('keyspace_misses', 0)
        total_requests = hits + misses
        
        # EXACT FORMULA FROM REQUIREMENTS:
        # hit_ratio = hits / (hits + misses) if total_requests > 0 else 0
        hit_ratio = hits / total_requests if total_requests > 0 else 0
        
        return {
            'hits': hits,
            'misses': misses,
            'hit_ratio': hit_ratio,
            'hit_ratio_percentage': round(hit_ratio * 100, 2),
            'total_operations': total_requests,
            'keyspace_hits': hits,
            'keyspace_misses': misses,
            'redis_version': redis_info.get('redis_version', 'unknown'),
        }
        
    except Exception as e:
        logger.error(f"Error retrieving Redis cache metrics: {e}")
        return {
            'hits': 0,
            'misses': 0,
            'hit_ratio': 0.0,
            'hit_ratio_percentage': 0.0,
            'total_operations': 0,
            'keyspace_hits': 0,
            'keyspace_misses': 0,
            'error': str(e),
        }


# Keep the original function but rename it
def get_redis_cache_metrics_original():
    """
    Original implementation - renamed to avoid conflicts.
    """
    return get_redis_cache_metrics_exact()


# Update the views to use the exact implementation
def get_redis_cache_metrics():
    """
    Main function that uses the exact formula from requirements.
    """
    return get_redis_cache_metrics_exact()