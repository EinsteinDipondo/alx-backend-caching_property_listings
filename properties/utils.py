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
            - redis_info: Additional Redis INFO data (optional)
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
        
        # Calculate total operations
        total_operations = keyspace_hits + keyspace_misses
        
        # Calculate hit and miss ratios (avoid division by zero)
        if total_operations > 0:
            hit_ratio = keyspace_hits / total_operations
            miss_ratio = keyspace_misses / total_operations
        else:
            hit_ratio = 0.0
            miss_ratio = 0.0
        
        # Prepare metrics dictionary
        metrics = {
            'hits': keyspace_hits,
            'misses': keyspace_misses,
            'hit_ratio': hit_ratio,
            'hit_ratio_percentage': round(hit_ratio * 100, 2),
            'miss_ratio': miss_ratio,
            'miss_ratio_percentage': round(miss_ratio * 100, 2),
            'total_operations': total_operations,
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
            f"Total Operations: {total_operations}"
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
            'keyspace_hits': 0,
            'keyspace_misses': 0,
            'error': str(e),
            'redis_version': 'unknown',
            'connected_clients': 0,
            'used_memory_human': '0B',
            'uptime_in_seconds': 0,
            'uptime_in_days': 0,
        }


def get_cache_effectiveness():
    """
    Analyze cache effectiveness based on hit ratio.
    
    Returns:
        dict: Cache effectiveness analysis including grade and recommendations
    """
    metrics = get_redis_cache_metrics()
    hit_ratio = metrics['hit_ratio']
    
    # Determine cache effectiveness grade
    if hit_ratio >= 0.9:
        grade = 'A+'
        effectiveness = 'Excellent'
        recommendation = 'Cache is working very effectively. Consider increasing cache TTL for even better performance.'
    elif hit_ratio >= 0.8:
        grade = 'A'
        effectiveness = 'Very Good'
        recommendation = 'Cache is effective. Monitor for any degradation.'
    elif hit_ratio >= 0.7:
        grade = 'B'
        effectiveness = 'Good'
        recommendation = 'Cache is working well. Consider optimizing cache keys or increasing cache duration.'
    elif hit_ratio >= 0.5:
        grade = 'C'
        effectiveness = 'Fair'
        recommendation = 'Cache effectiveness could be improved. Review cache strategies and TTL values.'
    elif hit_ratio >= 0.3:
        grade = 'D'
        effectiveness = 'Poor'
        recommendation = 'Cache is not very effective. Consider implementing more aggressive caching or reviewing cache keys.'
    else:
        grade = 'F'
        effectiveness = 'Very Poor'
        recommendation = 'Cache is ineffective. Consider redesigning caching strategy or investigating why cache misses are so high.'
    
    analysis = {
        'grade': grade,
        'effectiveness': effectiveness,
        'hit_ratio': hit_ratio,
        'hit_ratio_percentage': metrics['hit_ratio_percentage'],
        'recommendation': recommendation,
        'total_operations': metrics['total_operations'],
    }
    
    logger.info(
        f"Cache Effectiveness Analysis - "
        f"Grade: {grade}, "
        f"Effectiveness: {effectiveness}, "
        f"Hit Ratio: {hit_ratio:.2%}"
    )
    
    return analysis


def get_cache_keys_info():
    """
    Get information about cached keys in Redis.
    
    Returns:
        dict: Information about cache keys including count and samples
    """
    try:
        redis_conn = get_redis_connection("default")
        
        # Get all keys (use with caution in production with many keys)
        # In production, you might want to use SCAN instead of KEYS *
        all_keys = redis_conn.keys('*')
        
        # Count by key patterns
        key_patterns = {}
        property_keys = []
        other_keys = []
        
        for key in all_keys:
            key_str = key.decode('utf-8') if isinstance(key, bytes) else str(key)
            
            # Categorize keys
            if 'properties' in key_str.lower():
                property_keys.append(key_str)
                key_patterns['properties'] = key_patterns.get('properties', 0) + 1
            elif 'cache' in key_str.lower():
                key_patterns['cache'] = key_patterns.get('cache', 0) + 1
            elif 'session' in key_str.lower():
                key_patterns['session'] = key_patterns.get('session', 0) + 1
            else:
                other_keys.append(key_str)
                key_patterns['other'] = key_patterns.get('other', 0) + 1
        
        # Get TTL for some keys
        sample_ttls = {}
        sample_keys = property_keys[:5] + other_keys[:3]  # Sample first few keys
        
        for key in sample_keys:
            try:
                ttl = redis_conn.ttl(key)
                sample_ttls[key] = ttl
            except:
                sample_ttls[key] = 'N/A'
        
        keys_info = {
            'total_keys': len(all_keys),
            'key_patterns': key_patterns,
            'property_keys_count': len(property_keys),
            'property_keys_samples': property_keys[:10],  # First 10 property keys
            'sample_ttls': sample_ttls,
            'all_keys_count': len(all_keys),
        }
        
        logger.info(
            f"Cache Keys Info - "
            f"Total Keys: {len(all_keys)}, "
            f"Property Keys: {len(property_keys)}"
        )
        
        return keys_info
        
    except Exception as e:
        logger.error(f"Error retrieving cache keys info: {e}")
        return {
            'total_keys': 0,
            'key_patterns': {},
            'error': str(e)
        }


def reset_cache_metrics():
    """
    Reset Redis cache statistics (hits and misses).
    Note: This requires Redis >= 2.8.12 and CONFIG RESETSTAT command.
    
    Returns:
        bool: True if reset was successful, False otherwise
    """
    try:
        redis_conn = get_redis_connection("default")
        
        # Reset statistics
        redis_conn.config_resetstat()
        
        logger.info("Redis cache statistics reset successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error resetting cache metrics: {e}")
        return False


def monitor_cache_performance(sample_size=100):
    """
    Monitor cache performance by simulating requests.
    
    Args:
        sample_size (int): Number of simulated requests
        
    Returns:
        dict: Performance monitoring results
    """
    from django.core.cache import cache
    
    results = {
        'cache_hits': 0,
        'cache_misses': 0,
        'average_response_time': 0,
        'tests_performed': sample_size,
    }
    
    import time
    
    test_key_prefix = 'test_monitor_'
    total_time = 0
    
    for i in range(sample_size):
        key = f'{test_key_prefix}{i}'
        
        start_time = time.time()
        
        # Try to get from cache
        value = cache.get(key)
        
        if value is None:
            # Cache miss - simulate expensive operation
            results['cache_misses'] += 1
            time.sleep(0.001)  # Simulate work
            
            # Store in cache
            cache.set(key, f'value_{i}', 60)  # Cache for 60 seconds
        else:
            # Cache hit
            results['cache_hits'] += 1
        
        end_time = time.time()
        total_time += (end_time - start_time)
    
    # Calculate statistics
    results['average_response_time'] = total_time / sample_size
    results['hit_ratio'] = results['cache_hits'] / sample_size if sample_size > 0 else 0
    results['miss_ratio'] = results['cache_misses'] / sample_size if sample_size > 0 else 0
    
    # Clean up test keys
    for i in range(sample_size):
        cache.delete(f'{test_key_prefix}{i}')
    
    logger.info(
        f"Cache Performance Monitor - "
        f"Hits: {results['cache_hits']}, "
        f"Misses: {results['cache_misses']}, "
        f"Avg Time: {results['average_response_time']:.6f}s"
    )
    
    return results