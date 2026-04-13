"""Маршруты REST API (v1)."""
from django.urls import include, path

urlpatterns = [
    path('', include('SKLAD.urls')),
]
