from django.shortcuts import render
from django.views.decorators.cache import cache_page
from django.http import JsonResponse
from .models import Property
import json

# Cache this view for 15 minutes (60 * 15 = 900 seconds)
@cache_page(60 * 15)
def property_list(request):
    """
    View to return all properties with caching enabled for 15 minutes.
    """
    properties = Property.objects.all().order_by('-created_at')
    
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
    
    # Return JSON response
    return JsonResponse({
        'count': len(properties_data),
        'properties': properties_data,
        'message': 'This data is cached for 15 minutes'
    })

# Optional: A simple HTML view for browser testing
@cache_page(60 * 15)
def property_list_html(request):
    """
    HTML version of property list view with caching.
    """
    properties = Property.objects.all().order_by('-created_at')
    return render(request, 'properties/list.html', {
        'properties': properties,
        'cache_duration': '15 minutes'
    })