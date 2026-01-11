"""
URL configuration for alx-backend-caching_property_listings project.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('properties/', include('properties.urls')),  # Add this line
]