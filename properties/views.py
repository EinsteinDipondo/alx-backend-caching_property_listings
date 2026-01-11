from django.shortcuts import render
from django.views.decorators.cache import cache_page
from django.http import JsonResponse
from .models import Property
from .utils import get_all_properties, clear_properties_cache, get_property_count
import json
import time

# Cache the entire page response for 15 minutes
@cache_page(60 * 15)
def property_list(request):
    """
    View to return all properties using low-level caching for the queryset.
    This demonstrates two-level caching:
    1. Page-level caching: 15 minutes (@cache_page decorator)
    2. Queryset-level caching: 1 hour (get_all_properties() function)
    """
    start_time = time.time()
    
    # Get properties from cache or database (cached for 1 hour)
    properties = get_all_properties()
    
    # Calculate response time
    response_time = time.time() - start_time
    
    # Convert to list of dictionaries for JSON response
    properties_data = []
    for property in properties:
        properties_data.append({
            'id': property.id,
            'title': property.title,
            'description': property.description,
            'price': str(property.price),  # Convert Decimal to string
            'location': property.location,
            'created_at': property.created_at.isoformat(),
        })
    
    # Return JSON response with cache info
    return JsonResponse({
        'count': len(properties_data),
        'properties': properties_data,
        'cache_info': {
            'page_cache_duration': '15 minutes',
            'queryset_cache_duration': '1 hour',
            'response_time_seconds': round(response_time, 4),
            'source': 'cache' if response_time < 0.01 else 'database'
        },
        'message': 'Properties retrieved with low-level caching'
    })


# HTML view with caching
@cache_page(60 * 15)
def property_list_html(request):
    """
    HTML version of property list view using low-level caching.
    """
    properties = get_all_properties()
    property_count = get_property_count()
    
    return render(request, 'properties/list.html', {
        'properties': properties,
        'property_count': property_count,
        'page_cache_duration': '15 minutes',
        'queryset_cache_duration': '1 hour',
    })


# View to test and manage cache
def cache_info(request):
    """
    View to display cache information and manage cache.
    """
    from django.core.cache import cache
    
    cache_stats = {
        'all_properties_in_cache': cache.get('all_properties') is not None,
        'property_count_in_cache': cache.get('property_count') is not None,
        'cache_keys': list(cache.keys('*')) if hasattr(cache, 'keys') else ['keys() method not available'],
    }
    
    return JsonResponse({
        'cache_info': cache_stats,
        'endpoints': {
            'properties_json': '/properties/',
            'properties_html': '/properties/html/',
            'clear_cache': '/properties/clear-cache/',
            'cache_info': '/properties/cache-info/',
        }
    })


def clear_cache_view(request):
    """
    View to manually clear the properties cache.
    Useful for testing and development.
    """
    cleared = clear_properties_cache()
    
    return JsonResponse({
        'success': cleared,
        'message': 'Properties cache cleared successfully' if cleared else 'No properties cache to clear'
    })