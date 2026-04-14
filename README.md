# Складское приложение (Django + Vue)

Полноценное веб‑приложение для учёта складских запасов: категории, товары, поступления и списания.

## Что умеет система

- Регистрация и вход пользователей.
- Ведение справочника **категорий**.
- Ведение справочника **товаров** (SKU, единицы измерения, цены, остатки).
- Оформление документов **поступления** и **списания**.
- Работа с позициями документов (lines).
- Фильтрация, поиск и сортировка по API.
- Разделение данных по пользователям (пользователь видит только свои данные).

## Технологии

- **Backend:** Django 5, Django REST Framework, django-filter, TokenAuth
- **Frontend:** Vue 3, Vite, Pinia
- **DB:** SQLite (по умолчанию)

## Структура репозитория

```text
.
├── backend/                # Django API
│   ├── manage.py
│   ├── config/
│   └── SKLAD/
├── frontend/               # Vue-клиент
├── user_guide.md           # Руководство пользователя
├── requirements.txt        # Python-зависимости (корневой файл)
└── docs/
```

## Быстрый старт

### 1) Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate      # Linux/macOS
# .venv\Scripts\Activate.ps1   # Windows PowerShell
pip install -r ../requirements.txt
python manage.py migrate
python manage.py runserver
```

Backend будет доступен по адресу: `http://127.0.0.1:8000`

### 2) Frontend

В новом терминале:

```bash
cd frontend
npm install
npm run dev
```

Frontend обычно доступен по адресу: `http://127.0.0.1:5173`

## Основные API endpoints

Базовый префикс API: `http://127.0.0.1:8000/api/`

- `GET /health/` — проверка доступности.
- `POST /auth/register/` — регистрация.
- `POST /auth/login/` — вход.
- CRUD:
  - `/categories/`
  - `/products/`
  - `/receipts/`
  - `/receipt-lines/`
  - `/writeoffs/`
  - `/writeoff-lines/`

## Тесты

### Backend

```bash
cd backend
python manage.py test
```

### Frontend

```bash
cd frontend
npm test
```

## Важно

Ранее в проекте встречались описания как для Todo‑приложения. Актуальное назначение проекта — **складской учёт**.