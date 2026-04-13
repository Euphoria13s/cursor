from django.conf import settings
from django.db import models


class DocumentStatus(models.TextChoices):
    DRAFT = 'draft', 'Черновик'
    POSTED = 'posted', 'Проведён'
    CANCELLED = 'cancelled', 'Отменён'


class Category(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_categories',
        verbose_name='владелец',
        null=True,
        blank=True,
    )
    name = models.CharField('название', max_length=150)
    description = models.TextField('описание', blank=True)
    created_at = models.DateTimeField('создано', auto_now_add=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_products',
        verbose_name='владелец',
        null=True,
        blank=True,
    )
    name = models.CharField('наименование', max_length=200)
    sku = models.CharField('SKU', max_length=64, unique=True, db_index=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name='категория',
    )
    unit = models.CharField('ед. изм.', max_length=32)
    description = models.TextField('описание', blank=True)
    purchase_price = models.DecimalField(
        'закупочная цена',
        max_digits=12,
        decimal_places=2,
        default=0,
    )
    current_stock = models.DecimalField(
        'текущий остаток',
        max_digits=14,
        decimal_places=3,
        default=0,
    )
    min_stock = models.DecimalField(
        'минимальный запас',
        max_digits=14,
        decimal_places=3,
        default=0,
    )
    is_active = models.BooleanField('активен', default=True)
    created_at = models.DateTimeField('создано', auto_now_add=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self) -> str:
        return f'{self.name} ({self.sku})'


class Receipt(models.Model):
    document_number = models.CharField('номер документа', max_length=64, unique=True)
    receipt_date = models.DateField('дата поступления')
    supplier_name = models.CharField('поставщик', max_length=200)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='receipts_created',
        verbose_name='оформил',
    )
    comment = models.TextField('комментарий', blank=True)
    status = models.CharField(
        'статус',
        max_length=20,
        choices=DocumentStatus.choices,
        default=DocumentStatus.DRAFT,
    )
    created_at = models.DateTimeField('создано', auto_now_add=True)

    class Meta:
        ordering = ('-receipt_date', '-created_at')
        verbose_name = 'поступление'
        verbose_name_plural = 'поступления'

    def __str__(self) -> str:
        return f'Поступление {self.document_number} от {self.receipt_date}'


class ReceiptLine(models.Model):
    receipt = models.ForeignKey(
        Receipt,
        on_delete=models.CASCADE,
        related_name='lines',
        verbose_name='поступление',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='receipt_lines',
        verbose_name='товар',
    )
    quantity = models.DecimalField('количество', max_digits=14, decimal_places=3)
    unit_price = models.DecimalField('цена за ед.', max_digits=12, decimal_places=2)
    line_total = models.DecimalField('сумма строки', max_digits=14, decimal_places=2)

    class Meta:
        ordering = ('id',)
        verbose_name = 'позиция поступления'
        verbose_name_plural = 'позиции поступлений'

    def __str__(self) -> str:
        return f'{self.receipt.document_number}: {self.product.sku} × {self.quantity}'


class Writeoff(models.Model):
    document_number = models.CharField('номер документа', max_length=64, unique=True)
    writeoff_date = models.DateField('дата списания')
    reason = models.TextField('причина')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='writeoffs_created',
        verbose_name='оформил',
    )
    comment = models.TextField('комментарий', blank=True)
    status = models.CharField(
        'статус',
        max_length=20,
        choices=DocumentStatus.choices,
        default=DocumentStatus.DRAFT,
    )
    created_at = models.DateTimeField('создано', auto_now_add=True)

    class Meta:
        ordering = ('-writeoff_date', '-created_at')
        verbose_name = 'списание'
        verbose_name_plural = 'списания'

    def __str__(self) -> str:
        return f'Списание {self.document_number} от {self.writeoff_date}'


class WriteoffLine(models.Model):
    writeoff = models.ForeignKey(
        Writeoff,
        on_delete=models.CASCADE,
        related_name='lines',
        verbose_name='списание',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='writeoff_lines',
        verbose_name='товар',
    )
    quantity = models.DecimalField('количество', max_digits=14, decimal_places=3)
    unit_price = models.DecimalField('цена за ед.', max_digits=12, decimal_places=2)
    line_total = models.DecimalField('сумма строки', max_digits=14, decimal_places=2)

    class Meta:
        ordering = ('id',)
        verbose_name = 'позиция списания'
        verbose_name_plural = 'позиции списаний'

    def __str__(self) -> str:
        return f'{self.writeoff.document_number}: {self.product.sku} × {self.quantity}'
