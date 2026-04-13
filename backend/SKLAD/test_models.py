"""Unit-тесты моделей SKLAD."""

from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from SKLAD import models

User = get_user_model()


class CategoryModelTests(TestCase):
    def test_create_category(self):
        cat = models.Category.objects.create(name='Склад')
        self.assertEqual(cat.name, 'Склад')

    def test_category_str(self):
        cat = models.Category.objects.create(name='Электроника')
        self.assertEqual(str(cat), 'Электроника')

    def test_category_defaults(self):
        cat = models.Category.objects.create(name='Без описания')
        self.assertEqual(cat.description, '')
        self.assertIsNone(cat.owner)
        self.assertIsNotNone(cat.created_at)

    def test_category_owner_foreign_key(self):
        user = User.objects.create_user('cat_owner', password='pass12345')
        cat = models.Category.objects.create(name='Моя', owner=user)
        self.assertEqual(cat.owner, user)
        cat.refresh_from_db()
        self.assertEqual(cat.owner_id, user.pk)


class ProductModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('prod_owner', password='pass12345')
        self.category = models.Category.objects.create(name='Кат', owner=self.user)

    def test_create_product(self):
        p = models.Product.objects.create(
            owner=self.user,
            name='Товар',
            sku='SKU-PROD-1',
            category=self.category,
            unit='шт',
        )
        self.assertEqual(p.name, 'Товар')
        self.assertEqual(p.sku, 'SKU-PROD-1')

    def test_product_str(self):
        p = models.Product.objects.create(
            owner=self.user,
            name='Кабель',
            sku='SKU-CBL',
            category=self.category,
            unit='м',
        )
        self.assertEqual(str(p), 'Кабель (SKU-CBL)')

    def test_product_defaults(self):
        p = models.Product.objects.create(
            owner=self.user,
            name='Дефолты',
            sku='SKU-DEF',
            category=self.category,
            unit='шт',
        )
        self.assertTrue(p.is_active)
        self.assertEqual(p.purchase_price, Decimal('0'))
        self.assertEqual(p.current_stock, Decimal('0'))
        self.assertEqual(p.min_stock, Decimal('0'))
        self.assertEqual(p.description, '')

    def test_product_category_and_owner_foreign_key(self):
        p = models.Product.objects.create(
            owner=self.user,
            name='Связи',
            sku='SKU-FK',
            category=self.category,
            unit='шт',
        )
        self.assertEqual(p.category, self.category)
        self.assertEqual(p.owner, self.user)


class ReceiptModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('recv_user', password='pass12345')

    def test_create_receipt(self):
        r = models.Receipt.objects.create(
            document_number='R-100',
            receipt_date=date(2024, 6, 1),
            supplier_name='Поставщик',
            created_by=self.user,
        )
        self.assertEqual(r.document_number, 'R-100')

    def test_receipt_str(self):
        r = models.Receipt.objects.create(
            document_number='R-200',
            receipt_date=date(2024, 7, 15),
            supplier_name='X',
            created_by=self.user,
        )
        self.assertEqual(
            str(r),
            f'Поступление {r.document_number} от {r.receipt_date}',
        )

    def test_receipt_status_default_draft(self):
        r = models.Receipt.objects.create(
            document_number='R-DRAFT',
            receipt_date=date.today(),
            supplier_name='S',
            created_by=self.user,
        )
        self.assertEqual(r.status, models.DocumentStatus.DRAFT)

    def test_receipt_created_by_foreign_key(self):
        r = models.Receipt.objects.create(
            document_number='R-FK',
            receipt_date=date.today(),
            supplier_name='S',
            created_by=self.user,
        )
        self.assertEqual(r.created_by, self.user)


class ReceiptLineModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('line_user', password='pass12345')
        self.category = models.Category.objects.create(owner=self.user, name='C')
        self.product = models.Product.objects.create(
            owner=self.user,
            name='P',
            sku='SKU-LINE',
            category=self.category,
            unit='шт',
        )
        self.receipt = models.Receipt.objects.create(
            document_number='R-LINE',
            receipt_date=date.today(),
            supplier_name='S',
            created_by=self.user,
        )

    def test_create_receipt_line(self):
        line = models.ReceiptLine.objects.create(
            receipt=self.receipt,
            product=self.product,
            quantity=Decimal('2'),
            unit_price=Decimal('10.00'),
            line_total=Decimal('20.00'),
        )
        self.assertEqual(line.quantity, Decimal('2'))

    def test_receipt_line_str(self):
        line = models.ReceiptLine.objects.create(
            receipt=self.receipt,
            product=self.product,
            quantity=Decimal('3'),
            unit_price=Decimal('5.00'),
            line_total=Decimal('15.00'),
        )
        self.assertEqual(
            str(line),
            f'{self.receipt.document_number}: {self.product.sku} × {line.quantity}',
        )

    def test_receipt_line_foreign_keys(self):
        line = models.ReceiptLine.objects.create(
            receipt=self.receipt,
            product=self.product,
            quantity=Decimal('1'),
            unit_price=Decimal('1.00'),
            line_total=Decimal('1.00'),
        )
        self.assertEqual(line.receipt, self.receipt)
        self.assertEqual(line.product, self.product)

    def test_receipt_line_cascade_on_receipt_delete(self):
        line = models.ReceiptLine.objects.create(
            receipt=self.receipt,
            product=self.product,
            quantity=Decimal('1'),
            unit_price=Decimal('1.00'),
            line_total=Decimal('1.00'),
        )
        pk = line.pk
        self.receipt.delete()
        self.assertFalse(models.ReceiptLine.objects.filter(pk=pk).exists())


class WriteoffModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('wo_user', password='pass12345')

    def test_create_writeoff(self):
        w = models.Writeoff.objects.create(
            document_number='W-1',
            writeoff_date=date(2024, 8, 1),
            reason='Брак',
            created_by=self.user,
        )
        self.assertEqual(w.reason, 'Брак')

    def test_writeoff_str(self):
        w = models.Writeoff.objects.create(
            document_number='W-STR',
            writeoff_date=date(2024, 9, 1),
            reason='R',
            created_by=self.user,
        )
        self.assertEqual(
            str(w),
            f'Списание {w.document_number} от {w.writeoff_date}',
        )

    def test_writeoff_status_default_draft(self):
        w = models.Writeoff.objects.create(
            document_number='W-DR',
            writeoff_date=date.today(),
            reason='X',
            created_by=self.user,
        )
        self.assertEqual(w.status, models.DocumentStatus.DRAFT)

    def test_writeoff_created_by_foreign_key(self):
        w = models.Writeoff.objects.create(
            document_number='W-FK',
            writeoff_date=date.today(),
            reason='Y',
            created_by=self.user,
        )
        self.assertEqual(w.created_by, self.user)


class WriteoffLineModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('wol_user', password='pass12345')
        self.category = models.Category.objects.create(owner=self.user, name='WC')
        self.product = models.Product.objects.create(
            owner=self.user,
            name='WP',
            sku='SKU-WOL',
            category=self.category,
            unit='шт',
        )
        self.writeoff = models.Writeoff.objects.create(
            document_number='W-LINE',
            writeoff_date=date.today(),
            reason='Z',
            created_by=self.user,
        )

    def test_create_writeoff_line(self):
        line = models.WriteoffLine.objects.create(
            writeoff=self.writeoff,
            product=self.product,
            quantity=Decimal('1.5'),
            unit_price=Decimal('20.00'),
            line_total=Decimal('30.00'),
        )
        self.assertEqual(line.line_total, Decimal('30.00'))

    def test_writeoff_line_str(self):
        line = models.WriteoffLine.objects.create(
            writeoff=self.writeoff,
            product=self.product,
            quantity=Decimal('2'),
            unit_price=Decimal('3.00'),
            line_total=Decimal('6.00'),
        )
        self.assertEqual(
            str(line),
            f'{self.writeoff.document_number}: {self.product.sku} × {line.quantity}',
        )

    def test_writeoff_line_foreign_keys(self):
        line = models.WriteoffLine.objects.create(
            writeoff=self.writeoff,
            product=self.product,
            quantity=Decimal('1'),
            unit_price=Decimal('1.00'),
            line_total=Decimal('1.00'),
        )
        self.assertEqual(line.writeoff, self.writeoff)
        self.assertEqual(line.product, self.product)

    def test_writeoff_line_cascade_on_writeoff_delete(self):
        line = models.WriteoffLine.objects.create(
            writeoff=self.writeoff,
            product=self.product,
            quantity=Decimal('1'),
            unit_price=Decimal('1.00'),
            line_total=Decimal('1.00'),
        )
        pk = line.pk
        self.writeoff.delete()
        self.assertFalse(models.WriteoffLine.objects.filter(pk=pk).exists())
