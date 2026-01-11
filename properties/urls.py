from django.urls import path
from . import views

urlpatterns = [
    path('', views.property_list, name='property_list_json'),
    path('html/', views.property_list_html, name='property_list_html'),
]