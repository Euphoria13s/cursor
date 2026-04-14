from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import health, login, register
from .viewsets import (
    CategoryViewSet,
    ProductViewSet,
    ReceiptLineViewSet,
    ReceiptViewSet,
    WriteoffLineViewSet,
    WriteoffViewSet,
)

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('products', ProductViewSet, basename='product')
router.register('receipts', ReceiptViewSet, basename='receipt')
router.register('receipt-lines', ReceiptLineViewSet, basename='receiptline')
router.register('writeoffs', WriteoffViewSet, basename='writeoff')
router.register('writeoff-lines', WriteoffLineViewSet, basename='writeoffline')

urlpatterns = [
    path('auth/register/', register, name='register'),
    path('auth/login/', login, name='login'),
    path('health/', health, name='health'),
    path('', include(router.urls)),
]
    WriteoffLineViewSet,
    WriteoffViewSet,
)

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('products', ProductViewSet, basename='product')
router.register('receipts', ReceiptViewSet, basename='receipt')
router.register('receipt-lines', ReceiptLineViewSet, basename='receiptline')
router.register('writeoffs', WriteoffViewSet, basename='writeoff')
router.register('writeoff-lines', WriteoffLineViewSet, basename='writeoffline')

urlpatterns = [
    path('health/', health, name='health'),
    path('', include(router.urls)),
]
