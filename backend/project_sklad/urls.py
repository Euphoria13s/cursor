"""
Корневая маршрутизация project_sklad.
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('project_sklad.api_urls')),
]
