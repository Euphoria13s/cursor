from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated

from . import filters as sklad_filters
from . import models
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    ReceiptLineSerializer,
    ReceiptSerializer,
    WriteoffLineSerializer,
    WriteoffSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CategorySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = sklad_filters.CategoryFilter
    search_fields = ('name', 'description')
    ordering_fields = ('id', 'name', 'created_at')
    ordering = ('name',)

    def get_queryset(self):
        return models.Category.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = sklad_filters.ProductFilter
    search_fields = ('name', 'sku', 'description', 'unit')
    ordering_fields = (
        'id',
        'name',
        'sku',
        'purchase_price',
        'current_stock',
        'min_stock',
        'created_at',
    )
    ordering = ('name',)

    def get_queryset(self):
        return models.Product.objects.filter(owner=self.request.user).select_related(
            'category',
        )

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ReceiptViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ReceiptSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = sklad_filters.ReceiptFilter
    search_fields = (
        'document_number',
        'supplier_name',
        'comment',
    )
    ordering_fields = (
        'id',
        'document_number',
        'receipt_date',
        'status',
        'created_at',
    )
    ordering = ('-receipt_date', '-created_at')

    def get_queryset(self):
        return models.Receipt.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ReceiptLineViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ReceiptLineSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = sklad_filters.ReceiptLineFilter
    search_fields = (
        'product__name',
        'product__sku',
        'receipt__document_number',
    )
    ordering_fields = ('id', 'quantity', 'unit_price', 'line_total')
    ordering = ('id',)

    def get_queryset(self):
        return models.ReceiptLine.objects.filter(
            receipt__created_by=self.request.user,
        ).select_related('receipt', 'product')


class WriteoffViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = WriteoffSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = sklad_filters.WriteoffFilter
    search_fields = ('document_number', 'reason', 'comment')
    ordering_fields = (
        'id',
        'document_number',
        'writeoff_date',
        'status',
        'created_at',
    )
    ordering = ('-writeoff_date', '-created_at')

    def get_queryset(self):
        return models.Writeoff.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class WriteoffLineViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = WriteoffLineSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = sklad_filters.WriteoffLineFilter
    search_fields = (
        'product__name',
        'product__sku',
        'writeoff__document_number',
    )
    ordering_fields = ('id', 'quantity', 'unit_price', 'line_total')
    ordering = ('id',)

    def get_queryset(self):
        return models.WriteoffLine.objects.filter(
            writeoff__created_by=self.request.user,
        ).select_related('writeoff', 'product')
