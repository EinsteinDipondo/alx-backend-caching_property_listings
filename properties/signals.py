"""
Signal handlers for Property model cache invalidation.
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Property
import logging

# Set up logger
logger = logging.getLogger(__name__)

@receiver(post_save, sender=Property)
def invalidate_property_cache_on_save(sender, instance, **kwargs):
    """
    Invalidate cache when a Property is saved (created or updated).
    
    Args:
        sender: The model class (Property)
        instance: The actual instance being saved
        **kwargs: Additional signal arguments
    """
    cache_keys_to_delete = [
        'all_properties',          # Main properties cache
        'property_count',          # Property count cache
    ]
    
    deleted_keys = []
    for key in cache_keys_to_delete:
        if cache.delete(key):
            deleted_keys.append(key)
    
    if deleted_keys:
        logger.info(f"Cache invalidated on save for keys: {deleted_keys}")
        logger.info(f"Property '{instance.title}' was {'created' if kwargs.get('created') else 'updated'}")
    else:
        logger.debug("No cache to invalidate on save")


@receiver(post_delete, sender=Property)
def invalidate_property_cache_on_delete(sender, instance, **kwargs):
    """
    Invalidate cache when a Property is deleted.
    
    Args:
        sender: The model class (Property)
        instance: The actual instance being deleted
        **kwargs: Additional signal arguments
    """
    cache_keys_to_delete = [
        'all_properties',          # Main properties cache
        'property_count',          # Property count cache
    ]
    
    deleted_keys = []
    for key in cache_keys_to_delete:
        if cache.delete(key):
            deleted_keys.append(key)
    
    if deleted_keys:
        logger.info(f"Cache invalidated on delete for keys: {deleted_keys}")
        logger.info(f"Property '{instance.title}' was deleted")
    else:
        logger.debug("No cache to invalidate on delete")


def clear_all_property_related_cache():
    """
    Utility function to clear all property-related cache.
    Can be called from other parts of the application.
    """
    cache_patterns = [
        'all_properties',
        'property_count',
        ':1:views.decorators.cache.cache_page.*properties*',  # Page cache patterns
    ]
    
    cleared_count = 0
    
    # For simple keys
    for key in ['all_properties', 'property_count']:
        if cache.delete(key):
            cleared_count += 1
    
    # For pattern-based deletion (if supported by cache backend)
    try:
        # Redis supports pattern deletion
        if hasattr(cache, 'delete_pattern'):
            # Delete page cache entries for properties
            deleted = cache.delete_pattern(':1:views.decorators.cache.cache_page.*properties*')
            cleared_count += deleted
            if deleted:
                logger.info(f"Deleted {deleted} pattern-based cache entries")
    except AttributeError:
        # Pattern deletion not supported by this cache backend
        logger.debug("Pattern-based cache deletion not supported")
    
    logger.info(f"Cleared {cleared_count} property-related cache entries")
    return cleared_count