from rest_framework import serializers

from . import models


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = (
            'id',
            'owner',
            'name',
            'description',
            'created_at',
        )
        read_only_fields = ('id', 'created_at', 'owner')


class ProductSerializer(serializers.ModelSerializer):
    def validate_category(self, value: models.Category) -> models.Category:
        request = self.context.get('request')
        if (
            request is not None
            and value.owner_id is not None
            and value.owner_id != request.user.pk
        ):
            raise serializers.ValidationError('Категория не принадлежит текущему пользователю.')
        return value

    class Meta:
        model = models.Product
        fields = (
            'id',
            'owner',
            'name',
            'sku',
            'category',
            'unit',
            'description',
            'purchase_price',
            'current_stock',
            'min_stock',
            'is_active',
            'created_at',
        )
        read_only_fields = ('id', 'created_at', 'owner')


class ReceiptSerializer(serializers.ModelSerializer):
    """Поле author_name читается с связанного User через source (вызов get_full_name)."""

    author_name = serializers.CharField(
        label='имя автора',
        source='created_by.get_full_name',
        read_only=True,
    )

    class Meta:
        model = models.Receipt
        fields = (
            'id',
            'document_number',
            'receipt_date',
            'supplier_name',
            'created_by',
            'author_name',
            'comment',
            'status',
            'created_at',
        )
        read_only_fields = (
            'id',
            'created_at',
            'author_name',
            'created_by',
        )


class ReceiptLineSerializer(serializers.ModelSerializer):
    def validate_receipt(self, value: models.Receipt) -> models.Receipt:
        request = self.context.get('request')
        if request is not None and value.created_by_id != request.user.pk:
            raise serializers.ValidationError('Поступление не принадлежит текущему пользователю.')
        return value

    def validate_product(self, value: models.Product) -> models.Product:
        request = self.context.get('request')
        if (
            request is not None
            and value.owner_id is not None
            and value.owner_id != request.user.pk
        ):
            raise serializers.ValidationError('Товар не принадлежит текущему пользователю.')
        return value

    class Meta:
        model = models.ReceiptLine
        fields = (
            'id',
            'receipt',
            'product',
            'quantity',
            'unit_price',
            'line_total',
        )
        read_only_fields = ('id',)


class WriteoffSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(
        label='имя автора',
        source='created_by.get_full_name',
        read_only=True,
    )

    class Meta:
        model = models.Writeoff
        fields = (
            'id',
            'document_number',
            'writeoff_date',
            'reason',
            'created_by',
            'author_name',
            'comment',
            'status',
            'created_at',
        )
        read_only_fields = (
            'id',
            'created_at',
            'author_name',
            'created_by',
        )


class WriteoffLineSerializer(serializers.ModelSerializer):
    def validate_writeoff(self, value: models.Writeoff) -> models.Writeoff:
        request = self.context.get('request')
        if request is not None and value.created_by_id != request.user.pk:
            raise serializers.ValidationError('Списание не принадлежит текущему пользователю.')
        return value

    def validate_product(self, value: models.Product) -> models.Product:
        request = self.context.get('request')
        if (
            request is not None
            and value.owner_id is not None
            and value.owner_id != request.user.pk
        ):
            raise serializers.ValidationError('Товар не принадлежит текущему пользователю.')
        return value

    class Meta:
        model = models.WriteoffLine
        fields = (
            'id',
            'writeoff',
            'product',
            'quantity',
            'unit_price',
            'line_total',
        )
        read_only_fields = ('id',)
