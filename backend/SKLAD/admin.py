from django.contrib import admin

from . import models


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'name', 'description_short', 'created_at')
    list_filter = ('owner', ('created_at', admin.DateFieldListFilter))
    search_fields = ('name', 'description', 'owner__username')
    list_editable = ('name',)
    list_display_links = ('id',)
    autocomplete_fields = ('owner',)

    @admin.display(description='описание')
    def description_short(self, obj: models.Category) -> str:
        text = (obj.description or '').strip()
        return (text[:80] + '…') if len(text) > 80 else text or '—'


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'owner',
        'name',
        'sku',
        'category',
        'unit',
        'purchase_price',
        'current_stock',
        'min_stock',
        'is_active',
        'created_at',
    )
    list_filter = ('is_active', 'owner', 'category', ('created_at', admin.DateFieldListFilter))
    search_fields = ('name', 'sku', 'description', 'unit', 'owner__username')
    list_editable = ('min_stock', 'is_active')
    list_display_links = ('id', 'name')
    date_hierarchy = 'created_at'
    autocomplete_fields = ('category', 'owner')


@admin.register(models.ReceiptLine)
class ReceiptLineAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'receipt',
        'product',
        'quantity',
        'unit_price',
        'line_total',
    )
    list_filter = (
        'receipt__status',
        ('receipt__receipt_date', admin.DateFieldListFilter),
        'product__category',
    )
    search_fields = (
        'receipt__document_number',
        'receipt__supplier_name',
        'product__name',
        'product__sku',
    )
    list_editable = ('quantity', 'unit_price')
    list_display_links = ('id',)
    autocomplete_fields = ('receipt', 'product')


@admin.register(models.WriteoffLine)
class WriteoffLineAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'writeoff',
        'product',
        'quantity',
        'unit_price',
        'line_total',
    )
    list_filter = (
        'writeoff__status',
        ('writeoff__writeoff_date', admin.DateFieldListFilter),
        'product__category',
    )
    search_fields = (
        'writeoff__document_number',
        'writeoff__reason',
        'product__name',
        'product__sku',
    )
    list_editable = ('quantity', 'unit_price')
    list_display_links = ('id',)
    autocomplete_fields = ('writeoff', 'product')


class ReceiptLineInline(admin.TabularInline):
    model = models.ReceiptLine
    extra = 0
    autocomplete_fields = ('product',)


@admin.register(models.Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'document_number',
        'receipt_date',
        'supplier_name',
        'status',
        'created_by',
        'comment_short',
        'created_at',
    )
    list_filter = (
        'status',
        ('receipt_date', admin.DateFieldListFilter),
        'created_by',
    )
    search_fields = (
        'document_number',
        'supplier_name',
        'comment',
        'created_by__username',
        'created_by__first_name',
        'created_by__last_name',
    )
    list_editable = ('status',)
    list_display_links = ('id', 'document_number')
    date_hierarchy = 'receipt_date'
    autocomplete_fields = ('created_by',)
    inlines = (ReceiptLineInline,)

    @admin.display(description='комментарий')
    def comment_short(self, obj: models.Receipt) -> str:
        text = (obj.comment or '').strip()
        return (text[:60] + '…') if len(text) > 60 else text or '—'


class WriteoffLineInline(admin.TabularInline):
    model = models.WriteoffLine
    extra = 0
    autocomplete_fields = ('product',)


@admin.register(models.Writeoff)
class WriteoffAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'document_number',
        'writeoff_date',
        'status',
        'created_by',
        'reason_short',
        'comment_short',
        'created_at',
    )
    list_filter = (
        'status',
        ('writeoff_date', admin.DateFieldListFilter),
        'created_by',
    )
    search_fields = (
        'document_number',
        'reason',
        'comment',
        'created_by__username',
        'created_by__first_name',
        'created_by__last_name',
    )
    list_editable = ('status',)
    list_display_links = ('id', 'document_number')
    date_hierarchy = 'writeoff_date'
    autocomplete_fields = ('created_by',)
    inlines = (WriteoffLineInline,)

    @admin.display(description='причина')
    def reason_short(self, obj: models.Writeoff) -> str:
        text = (obj.reason or '').strip()
        return (text[:60] + '…') if len(text) > 60 else text or '—'

    @admin.display(description='комментарий')
    def comment_short(self, obj: models.Writeoff) -> str:
        text = (obj.comment or '').strip()
        return (text[:60] + '…') if len(text) > 60 else text or '—'