"""
Заполнение БД демонстрационными данными: 3 пользователя и набор сущностей на каждого.
Повторный запуск удаляет предыдущие данные с теми же учётными записями seed_*.
"""

from __future__ import annotations

import random
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from SKLAD.models import (
    Category,
    DocumentStatus,
    Product,
    Receipt,
    ReceiptLine,
    Writeoff,
    WriteoffLine,
)

SEED_USERNAMES = ('seed_alpha', 'seed_beta', 'seed_gamma')
SEED_PASSWORD = 'seedpass2026'

SUPPLIERS = (
    'ООО «Снабжение»',
    'ИП Кузнецов',
    'ТД Регион',
    'Альфа-опт',
    'Вектор поставка',
    'Глобал Трейд',
)
UNITS = ('шт', 'кг', 'л', 'уп', 'м', 'компл')
REASONS = (
    'Порча при хранении',
    'Истечение срока годности',
    'Инвентаризационная недостача',
    'Производственный брак',
    'Пересорт',
)


def _money(a: float, b: float) -> Decimal:
    return Decimal(str(round(random.uniform(a, b), 2)))


def _qty(a: float, b: float) -> Decimal:
    return Decimal(str(round(random.uniform(a, b), 3)))


def _clear_seed_users(usernames: tuple[str, ...]) -> None:
    User = get_user_model()
    qs = User.objects.filter(username__in=usernames)
    if not qs.exists():
        return
    WriteoffLine.objects.filter(writeoff__created_by__in=qs).delete()
    Writeoff.objects.filter(created_by__in=qs).delete()
    ReceiptLine.objects.filter(receipt__created_by__in=qs).delete()
    Receipt.objects.filter(created_by__in=qs).delete()
    Product.objects.filter(owner__in=qs).delete()
    Category.objects.filter(owner__in=qs).delete()
    qs.delete()


class Command(BaseCommand):
    help = (
        'Создаёт 3 пользователей (seed_alpha, seed_beta, seed_gamma) и для каждого '
        '5–10 категорий и товаров, документы поступления/списания со строками и разными статусами.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-clear',
            action='store_true',
            help='Не удалять существующих seed-пользователей перед заполнением (может вызвать ошибку уникальности).',
        )

    def handle(self, *args, **options):
        random.seed()

        if not options['no_clear']:
            _clear_seed_users(SEED_USERNAMES)
            self.stdout.write(self.style.WARNING('Удалены предыдущие данные seed_alpha / seed_beta / seed_gamma.'))

        User = get_user_model()
        created_total = 0

        with transaction.atomic():
            users = []
            for username in SEED_USERNAMES:
                u = User.objects.create_user(
                    username=username,
                    password=SEED_PASSWORD,
                    email=f'{username}@seed.local',
                    first_name=random.choice(('Иван', 'Мария', 'Алексей', 'Елена', 'Дмитрий')),
                    last_name=random.choice(('Петров', 'Сидорова', 'Козлов', 'Новикова', 'Орлов')),
                )
                users.append(u)
                created_total += 1

            for user in users:
                created_total += self._seed_for_user(user)

        self.stdout.write(self.style.SUCCESS(f'Готово. Создано записей (суммарно сущностей): {created_total}'))
        self.stdout.write(f'Пароль для всех seed-пользователей: {SEED_PASSWORD}')

    def _seed_for_user(self, user) -> int:
        n = 0
        n_cat = random.randint(5, 10)
        n_prod = random.randint(5, 10)

        categories: list[Category] = []
        for i in range(n_cat):
            cat = Category.objects.create(
                owner=user,
                name=f'Категория {user.username}_{i}_{random.randint(10, 99)}',
                description=random.choice(('', 'Оптовая группа', 'Розница', 'Сезонные позиции', 'Расходники')),
            )
            categories.append(cat)
            n += 1

        products: list[Product] = []
        for i in range(n_prod):
            sku = f'{user.pk}-{i}-{random.randint(10000, 99999)}'[:64]
            p = Product.objects.create(
                owner=user,
                name=f'Товар {user.username[:5]} {random.choice(("А", "Б", "В"))}-{i}',
                sku=sku,
                category=random.choice(categories),
                unit=random.choice(UNITS),
                description=random.choice(('', 'Стандартная номенклатура', 'Импорт')),
                purchase_price=_money(10, 5000),
                current_stock=_qty(0, 500),
                min_stock=_qty(1, 50),
                is_active=random.choice((True, True, True, False)),
            )
            products.append(p)
            n += 1

        n_receipts = random.randint(2, 5)
        for i in range(n_receipts):
            doc_no = f'IN-{user.pk}-{i}-{random.randint(1000, 9999)}'
            r = Receipt.objects.create(
                document_number=doc_no,
                receipt_date=date.today() - timedelta(days=random.randint(0, 120)),
                supplier_name=random.choice(SUPPLIERS),
                created_by=user,
                comment=random.choice(('', 'Срочная поставка', 'По договору №…')),
                status=random.choice([s.value for s in DocumentStatus]),
            )
            n += 1
            for _ in range(random.randint(1, 4)):
                prod = random.choice(products)
                q = _qty(1, 100)
                up = _money(50, 2000)
                total = (q * up).quantize(Decimal('0.01'))
                ReceiptLine.objects.create(
                    receipt=r,
                    product=prod,
                    quantity=q,
                    unit_price=up,
                    line_total=total,
                )
                n += 1

        n_writeoffs = random.randint(2, 5)
        for i in range(n_writeoffs):
            doc_no = f'OUT-{user.pk}-{i}-{random.randint(1000, 9999)}'
            w = Writeoff.objects.create(
                document_number=doc_no,
                writeoff_date=date.today() - timedelta(days=random.randint(0, 90)),
                reason=random.choice(REASONS),
                created_by=user,
                comment=random.choice(('', 'Согласовано', 'Акт комиссии')),
                status=random.choice([s.value for s in DocumentStatus]),
            )
            n += 1
            for _ in range(random.randint(1, 3)):
                prod = random.choice(products)
                q = _qty(0.5, 30)
                up = _money(50, 1500)
                total = (q * up).quantize(Decimal('0.01'))
                WriteoffLine.objects.create(
                    writeoff=w,
                    product=prod,
                    quantity=q,
                    unit_price=up,
                    line_total=total,
                )
                n += 1

        return n
