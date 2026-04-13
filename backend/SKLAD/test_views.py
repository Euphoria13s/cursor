"""Интеграционные тесты API (ViewSet) с APITestCase и APIClient."""

from datetime import date
from decimal import Decimal
import uuid

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from SKLAD import models

User = get_user_model()


def _anon_client():
    return APIClient()


class CategoryViewSetAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user('api_cat', password='pass12345')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_list_200(self):
        models.Category.objects.create(owner=self.user, name='A')
        r = self.client.get('/api/categories/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertIn('results', r.data)

    def test_create_201(self):
        r = self.client.post(
            '/api/categories/',
            {'name': 'Новая', 'description': ''},
            format='json',
        )
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(r.data['name'], 'Новая')
        self.assertEqual(
            models.Category.objects.get(pk=r.data['id']).owner,
            self.user,
        )

    def test_patch_200(self):
        c = models.Category.objects.create(owner=self.user, name='Old')
        r = self.client.patch(
            f'/api/categories/{c.pk}/',
            {'description': 'Обновлено'},
            format='json',
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        c.refresh_from_db()
        self.assertEqual(c.description, 'Обновлено')

    def test_delete_204(self):
        c = models.Category.objects.create(owner=self.user, name='Удалить')
        r = self.client.delete(f'/api/categories/{c.pk}/')
        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(models.Category.objects.filter(pk=c.pk).exists())

    def test_list_without_token_401(self):
        r = _anon_client().get('/api/categories/')
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_detail_missing_404(self):
        r = self.client.get('/api/categories/999999999/')
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)

    def test_filter_by_name_icontains(self):
        models.Category.objects.create(owner=self.user, name='AlphaBeta')
        models.Category.objects.create(owner=self.user, name='Other')
        r = self.client.get('/api/categories/', {'name__icontains': 'Alpha'})
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        names = {row['name'] for row in r.data['results']}
        self.assertIn('AlphaBeta', names)
        self.assertNotIn('Other', names)


class ProductViewSetAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user('api_prod', password='pass12345')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.category = models.Category.objects.create(
            owner=self.user,
            name='Категория',
        )
        self.sku = f'SKU-{uuid.uuid4().hex[:10]}'

    def test_list_200(self):
        models.Product.objects.create(
            owner=self.user,
            name='P',
            sku=self.sku,
            category=self.category,
            unit='шт',
        )
        r = self.client.get('/api/products/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertIn('results', r.data)

    def test_create_201(self):
        sku_new = f'SKU-{uuid.uuid4().hex[:10]}'
        r = self.client.post(
            '/api/products/',
            {
                'name': 'Товар API',
                'sku': sku_new,
                'category': self.category.pk,
                'unit': 'шт',
                'description': '',
                'purchase_price': '10.00',
                'current_stock': '0',
                'min_stock': '0',
                'is_active': True,
            },
            format='json',
        )
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(r.data['sku'], sku_new)

    def test_patch_200(self):
        p = models.Product.objects.create(
            owner=self.user,
            name='Was',
            sku=f'SKU-{uuid.uuid4().hex[:10]}',
            category=self.category,
            unit='шт',
        )
        r = self.client.patch(
            f'/api/products/{p.pk}/',
            {'name': 'Стало'},
            format='json',
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        p.refresh_from_db()
        self.assertEqual(p.name, 'Стало')

    def test_delete_204(self):
        p = models.Product.objects.create(
            owner=self.user,
            name='Удаляемый',
            sku=f'SKU-{uuid.uuid4().hex[:10]}',
            category=self.category,
            unit='шт',
        )
        r = self.client.delete(f'/api/products/{p.pk}/')
        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)

    def test_list_without_token_401(self):
        r = _anon_client().get('/api/products/')
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_detail_missing_404(self):
        r = self.client.get('/api/products/999999999/')
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)

    def test_filter_is_active(self):
        models.Product.objects.create(
            owner=self.user,
            name='Active',
            sku=f'A-{uuid.uuid4().hex[:8]}',
            category=self.category,
            unit='шт',
            is_active=True,
        )
        models.Product.objects.create(
            owner=self.user,
            name='Inactive',
            sku=f'I-{uuid.uuid4().hex[:8]}',
            category=self.category,
            unit='шт',
            is_active=False,
        )
        r = self.client.get('/api/products/', {'is_active': 'true'})
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        names = {row['name'] for row in r.data['results']}
        self.assertIn('Active', names)
        self.assertNotIn('Inactive', names)


class ReceiptViewSetAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user('api_rec', password='pass12345')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.doc = f'R-{uuid.uuid4().hex[:12]}'

    def test_list_200(self):
        models.Receipt.objects.create(
            document_number=self.doc,
            receipt_date=date.today(),
            supplier_name='S',
            created_by=self.user,
        )
        r = self.client.get('/api/receipts/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertIn('results', r.data)

    def test_create_201(self):
        doc = f'R-{uuid.uuid4().hex[:12]}'
        r = self.client.post(
            '/api/receipts/',
            {
                'document_number': doc,
                'receipt_date': str(date.today()),
                'supplier_name': 'Поставщик',
                'comment': '',
                'status': models.DocumentStatus.DRAFT,
            },
            format='json',
        )
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(r.data['document_number'], doc)

    def test_patch_200(self):
        rec = models.Receipt.objects.create(
            document_number=f'R-{uuid.uuid4().hex[:12]}',
            receipt_date=date.today(),
            supplier_name='S',
            created_by=self.user,
        )
        r = self.client.patch(
            f'/api/receipts/{rec.pk}/',
            {'comment': 'Правка'},
            format='json',
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        rec.refresh_from_db()
        self.assertEqual(rec.comment, 'Правка')

    def test_delete_204(self):
        rec = models.Receipt.objects.create(
            document_number=f'R-{uuid.uuid4().hex[:12]}',
            receipt_date=date.today(),
            supplier_name='S',
            created_by=self.user,
        )
        r = self.client.delete(f'/api/receipts/{rec.pk}/')
        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)

    def test_list_without_token_401(self):
        r = _anon_client().get('/api/receipts/')
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_detail_missing_404(self):
        r = self.client.get('/api/receipts/999999999/')
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)

    def test_filter_status(self):
        d1 = f'R-{uuid.uuid4().hex[:10]}'
        d2 = f'R-{uuid.uuid4().hex[:10]}'
        models.Receipt.objects.create(
            document_number=d1,
            receipt_date=date.today(),
            supplier_name='S',
            created_by=self.user,
            status=models.DocumentStatus.DRAFT,
        )
        models.Receipt.objects.create(
            document_number=d2,
            receipt_date=date.today(),
            supplier_name='S',
            created_by=self.user,
            status=models.DocumentStatus.POSTED,
        )
        r = self.client.get('/api/receipts/', {'status': models.DocumentStatus.DRAFT})
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        nums = {row['document_number'] for row in r.data['results']}
        self.assertIn(d1, nums)
        self.assertNotIn(d2, nums)


class ReceiptLineViewSetAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user('api_rl', password='pass12345')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.category = models.Category.objects.create(owner=self.user, name='C')
        self.product = models.Product.objects.create(
            owner=self.user,
            name='P',
            sku=f'SKU-{uuid.uuid4().hex[:10]}',
            category=self.category,
            unit='шт',
        )
        self.receipt = models.Receipt.objects.create(
            document_number=f'R-{uuid.uuid4().hex[:12]}',
            receipt_date=date.today(),
            supplier_name='S',
            created_by=self.user,
        )

    def test_list_200(self):
        models.ReceiptLine.objects.create(
            receipt=self.receipt,
            product=self.product,
            quantity=Decimal('1'),
            unit_price=Decimal('1.00'),
            line_total=Decimal('1.00'),
        )
        r = self.client.get('/api/receipt-lines/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertIn('results', r.data)

    def test_create_201(self):
        r = self.client.post(
            '/api/receipt-lines/',
            {
                'receipt': self.receipt.pk,
                'product': self.product.pk,
                'quantity': '2.000',
                'unit_price': '5.00',
                'line_total': '10.00',
            },
            format='json',
        )
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_patch_200(self):
        line = models.ReceiptLine.objects.create(
            receipt=self.receipt,
            product=self.product,
            quantity=Decimal('1'),
            unit_price=Decimal('1.00'),
            line_total=Decimal('1.00'),
        )
        r = self.client.patch(
            f'/api/receipt-lines/{line.pk}/',
            {'quantity': '3.000', 'line_total': '3.00'},
            format='json',
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        line.refresh_from_db()
        self.assertEqual(line.quantity, Decimal('3'))

    def test_delete_204(self):
        line = models.ReceiptLine.objects.create(
            receipt=self.receipt,
            product=self.product,
            quantity=Decimal('1'),
            unit_price=Decimal('1.00'),
            line_total=Decimal('1.00'),
        )
        r = self.client.delete(f'/api/receipt-lines/{line.pk}/')
        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)

    def test_list_without_token_401(self):
        r = _anon_client().get('/api/receipt-lines/')
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_detail_missing_404(self):
        r = self.client.get('/api/receipt-lines/999999999/')
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)

    def test_filter_by_receipt(self):
        rec2 = models.Receipt.objects.create(
            document_number=f'R-{uuid.uuid4().hex[:12]}',
            receipt_date=date.today(),
            supplier_name='S2',
            created_by=self.user,
        )
        l1 = models.ReceiptLine.objects.create(
            receipt=self.receipt,
            product=self.product,
            quantity=Decimal('1'),
            unit_price=Decimal('1.00'),
            line_total=Decimal('1.00'),
        )
        models.ReceiptLine.objects.create(
            receipt=rec2,
            product=self.product,
            quantity=Decimal('1'),
            unit_price=Decimal('1.00'),
            line_total=Decimal('1.00'),
        )
        r = self.client.get('/api/receipt-lines/', {'receipt': self.receipt.pk})
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        ids = {row['id'] for row in r.data['results']}
        self.assertIn(l1.pk, ids)


class WriteoffViewSetAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user('api_wo', password='pass12345')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_list_200(self):
        models.Writeoff.objects.create(
            document_number=f'W-{uuid.uuid4().hex[:12]}',
            writeoff_date=date.today(),
            reason='R',
            created_by=self.user,
        )
        r = self.client.get('/api/writeoffs/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertIn('results', r.data)

    def test_create_201(self):
        doc = f'W-{uuid.uuid4().hex[:12]}'
        r = self.client.post(
            '/api/writeoffs/',
            {
                'document_number': doc,
                'writeoff_date': str(date.today()),
                'reason': 'Порча',
                'comment': '',
                'status': models.DocumentStatus.DRAFT,
            },
            format='json',
        )
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(r.data['document_number'], doc)

    def test_patch_200(self):
        w = models.Writeoff.objects.create(
            document_number=f'W-{uuid.uuid4().hex[:12]}',
            writeoff_date=date.today(),
            reason='R',
            created_by=self.user,
        )
        r = self.client.patch(
            f'/api/writeoffs/{w.pk}/',
            {'comment': 'Коммент'},
            format='json',
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        w.refresh_from_db()
        self.assertEqual(w.comment, 'Коммент')

    def test_delete_204(self):
        w = models.Writeoff.objects.create(
            document_number=f'W-{uuid.uuid4().hex[:12]}',
            writeoff_date=date.today(),
            reason='R',
            created_by=self.user,
        )
        r = self.client.delete(f'/api/writeoffs/{w.pk}/')
        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)

    def test_list_without_token_401(self):
        r = _anon_client().get('/api/writeoffs/')
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_detail_missing_404(self):
        r = self.client.get('/api/writeoffs/999999999/')
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)

    def test_filter_status(self):
        d1 = f'W-{uuid.uuid4().hex[:10]}'
        d2 = f'W-{uuid.uuid4().hex[:10]}'
        models.Writeoff.objects.create(
            document_number=d1,
            writeoff_date=date.today(),
            reason='R',
            created_by=self.user,
            status=models.DocumentStatus.DRAFT,
        )
        models.Writeoff.objects.create(
            document_number=d2,
            writeoff_date=date.today(),
            reason='R',
            created_by=self.user,
            status=models.DocumentStatus.CANCELLED,
        )
        r = self.client.get('/api/writeoffs/', {'status': models.DocumentStatus.DRAFT})
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        nums = {row['document_number'] for row in r.data['results']}
        self.assertIn(d1, nums)
        self.assertNotIn(d2, nums)


class WriteoffLineViewSetAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user('api_wol', password='pass12345')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.category = models.Category.objects.create(owner=self.user, name='C')
        self.product = models.Product.objects.create(
            owner=self.user,
            name='P',
            sku=f'SKU-{uuid.uuid4().hex[:10]}',
            category=self.category,
            unit='шт',
        )
        self.writeoff = models.Writeoff.objects.create(
            document_number=f'W-{uuid.uuid4().hex[:12]}',
            writeoff_date=date.today(),
            reason='R',
            created_by=self.user,
        )

    def test_list_200(self):
        models.WriteoffLine.objects.create(
            writeoff=self.writeoff,
            product=self.product,
            quantity=Decimal('1'),
            unit_price=Decimal('1.00'),
            line_total=Decimal('1.00'),
        )
        r = self.client.get('/api/writeoff-lines/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertIn('results', r.data)

    def test_create_201(self):
        r = self.client.post(
            '/api/writeoff-lines/',
            {
                'writeoff': self.writeoff.pk,
                'product': self.product.pk,
                'quantity': '1.000',
                'unit_price': '2.00',
                'line_total': '2.00',
            },
            format='json',
        )
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_patch_200(self):
        line = models.WriteoffLine.objects.create(
            writeoff=self.writeoff,
            product=self.product,
            quantity=Decimal('1'),
            unit_price=Decimal('1.00'),
            line_total=Decimal('1.00'),
        )
        r = self.client.patch(
            f'/api/writeoff-lines/{line.pk}/',
            {'quantity': '4.000', 'line_total': '4.00'},
            format='json',
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        line.refresh_from_db()
        self.assertEqual(line.quantity, Decimal('4'))

    def test_delete_204(self):
        line = models.WriteoffLine.objects.create(
            writeoff=self.writeoff,
            product=self.product,
            quantity=Decimal('1'),
            unit_price=Decimal('1.00'),
            line_total=Decimal('1.00'),
        )
        r = self.client.delete(f'/api/writeoff-lines/{line.pk}/')
        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)

    def test_list_without_token_401(self):
        r = _anon_client().get('/api/writeoff-lines/')
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_detail_missing_404(self):
        r = self.client.get('/api/writeoff-lines/999999999/')
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)

    def test_filter_by_writeoff(self):
        w2 = models.Writeoff.objects.create(
            document_number=f'W-{uuid.uuid4().hex[:12]}',
            writeoff_date=date.today(),
            reason='R2',
            created_by=self.user,
        )
        l1 = models.WriteoffLine.objects.create(
            writeoff=self.writeoff,
            product=self.product,
            quantity=Decimal('1'),
            unit_price=Decimal('1.00'),
            line_total=Decimal('1.00'),
        )
        models.WriteoffLine.objects.create(
            writeoff=w2,
            product=self.product,
            quantity=Decimal('1'),
            unit_price=Decimal('1.00'),
            line_total=Decimal('1.00'),
        )
        r = self.client.get('/api/writeoff-lines/', {'writeoff': self.writeoff.pk})
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        ids = {row['id'] for row in r.data['results']}
        self.assertIn(l1.pk, ids)
