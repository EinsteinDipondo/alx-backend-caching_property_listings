from django.urls import path
from . import views

urlpatterns = [
    # Main property endpoints
    path('', views.property_list, name='property_list_json'),
    path('html/', views.property_list_html, name='property_list_html'),
    
    # Cache management endpoints
    path('cache-info/', views.cache_info, name='cache_info'),
    path('clear-cache/', views.clear_cache_view, name='clear_cache'),
    path('cache-status/', views.test_cache_status, name='cache_status'),
    
    # Signal testing endpoints
    path('create-test/', views.create_property_test, name='create_property_test'),
    path('delete-test/<int:property_id>/', views.delete_property_test, name='delete_property_test'),
]