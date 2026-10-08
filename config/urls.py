"""
Config URL Configuration for U Kost.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('ukost.urls')),
]
