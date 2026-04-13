from django.urls import path

from . import views

app_name = 'catalog'

urlpatterns = [
    path('health/', views.health, name='health'),
]
