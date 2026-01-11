from django.shortcuts import render
from django.views.decorators.cache import cache_page
from django.http import JsonResponse
from .models import Property
from .utils import get_all_properties, clear_properties_cache, get_property_count
import json
import time
# Add these imports at the top if not already there
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Property
from .forms import PropertyForm  # We'll create this next
from django.core.cache import cache

# Add these views at the bottom of views.py
def create_property_test(request):
    """
    Test view to create a property and see cache invalidation in action.
    """
    if request.method == 'POST':
        title = request.POST.get('title', 'Test Property')
        description = request.POST.get('description', 'Test Description')
        price = request.POST.get('price', '100000.00')
        location = request.POST.get('location', 'Test Location')
        
        # Create property (this should trigger the signal)
        property = Property.objects.create(
            title=title,
            description=description,
            price=price,
            location=location
        )
        
        return render(request, 'properties/create_success.html', {
            'property': property,
            'cache_cleared': cache.get('all_properties') is None
        })
    
    return render(request, 'properties/create_form.html')


def delete_property_test(request, property_id):
    """
    Test view to delete a property and see cache invalidation.
    """
    try:
        property = Property.objects.get(id=property_id)
        cache_before = cache.get('all_properties') is not None
        
        # Delete property (this should trigger the signal)
        property.delete()
        
        cache_after = cache.get('all_properties') is not None
        
        return render(request, 'properties/delete_success.html', {
            'property_title': property.title,
            'cache_cleared': cache_before and not cache_after
        })
    except Property.DoesNotExist:
        return HttpResponse("Property not found", status=404)


def test_cache_status(request):
    """
    View to check current cache status and manually trigger cache clearing.
    """
    from .signals import clear_all_property_related_cache
    
    cache_status = {
        'all_properties_cached': cache.get('all_properties') is not None,
        'property_count_cached': cache.get('property_count') is not None,
        'cache_backend': str(cache),
    }
    
    if request.method == 'POST' and 'clear_cache' in request.POST:
        cleared = clear_all_property_related_cache()
        cache_status['last_cleared'] = cleared
        cache_status['message'] = f'Cleared {cleared} cache entries'
    
    return render(request, 'properties/cache_status.html', {
        'cache_status': cache_status,
        'properties_count': Property.objects.count()
    })

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