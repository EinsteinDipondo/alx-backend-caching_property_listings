from django.apps import AppConfig


class PropertiesConfig(AppConfig):
    """
    App configuration for properties app with signal registration.
    """
    
    # Use BigAutoField as default for model primary keys
    default_auto_field = 'django.db.models.BigAutoField'
    
    # App name
    name = 'properties'
    
    def ready(self):
        """
        Override ready() to import signals when Django starts.
        This ensures signal handlers are connected.
        """
        # Import signal handlers
        import properties.signals
        
        # Log that signals are loaded (for debugging)
        import logging
        logger = logging.getLogger(__name__)
        logger.info("Properties app ready: signals loaded")
        
        # You can also connect signals manually here if needed:
        # from django.db.models.signals import post_save, post_delete
        # from .models import Property
        # from .signals import invalidate_property_cache_on_save, invalidate_property_cache_on_delete
        
        # post_save.connect(invalidate_property_cache_on_save, sender=Property)
        # post_delete.connect(invalidate_property_cache_on_delete, sender=Property)