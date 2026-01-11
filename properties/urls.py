from django.urls import path
from . import views

urlpatterns = [
    # Main property endpoints
    path('', views.property_list, name='property_list_json'),
    path('html/', views.property_list_html, name='property_list_html'),
    
    # Cache management endpoints (for testing)
    path('cache-info/', views.cache_info, name='cache_info'),
    path('clear-cache/', views.clear_cache_view, name='clear_cache'),
]