from django_filters import rest_framework as filters

from . import models


class CategoryFilter(filters.FilterSet):
    class Meta:
        model = models.Category
        fields = {
            'name': ['exact', 'icontains'],
            'created_at': ['date', 'gte', 'lte'],
        }


class ProductFilter(filters.FilterSet):
    class Meta:
        model = models.Product
        fields = {
            'name': ['exact', 'icontains'],
            'sku': ['exact', 'icontains'],
            'category': ['exact'],
            'is_active': ['exact'],
            'current_stock': ['exact', 'gte', 'lte'],
            'min_stock': ['exact', 'gte', 'lte'],
            'purchase_price': ['exact', 'gte', 'lte'],
            'created_at': ['date', 'gte', 'lte'],
        }


class ReceiptFilter(filters.FilterSet):
    class Meta:
        model = models.Receipt
        fields = {
            'document_number': ['exact', 'icontains'],
            'status': ['exact'],
            'receipt_date': ['exact', 'gte', 'lte'],
            'supplier_name': ['exact', 'icontains'],
            'created_by': ['exact'],
            'created_at': ['date', 'gte', 'lte'],
        }


class ReceiptLineFilter(filters.FilterSet):
    class Meta:
        model = models.ReceiptLine
        fields = {
            'receipt': ['exact'],
            'product': ['exact'],
            'quantity': ['exact', 'gte', 'lte'],
        }


class WriteoffFilter(filters.FilterSet):
    class Meta:
        model = models.Writeoff
        fields = {
            'document_number': ['exact', 'icontains'],
            'status': ['exact'],
            'writeoff_date': ['exact', 'gte', 'lte'],
            'created_at': ['date', 'gte', 'lte'],
        }


class WriteoffLineFilter(filters.FilterSet):
    class Meta:
        model = models.WriteoffLine
        fields = {
            'writeoff': ['exact'],
            'product': ['exact'],
            'quantity': ['exact', 'gte', 'lte'],
        }
