# Backend (Django REST API)

Серверная часть складского приложения.

## Запуск

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r ../requirements.txt
python manage.py migrate
python manage.py runserver
```

## Базовый URL API

- `http://127.0.0.1:8000/api/`

## Ключевые маршруты

- `GET /api/health/`
- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `CRUD /api/categories/`
- `CRUD /api/products/`
- `CRUD /api/receipts/`
- `CRUD /api/receipt-lines/`
- `CRUD /api/writeoffs/`
- `CRUD /api/writeoff-lines/`