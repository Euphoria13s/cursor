from django.urls import path

from . import views

app_name = 'inventory'

urlpatterns = [
    path('health/', views.health, name='health'),
]
