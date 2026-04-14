# Fullstack Todo App

Веб-приложение для управления задачами с REST API на Django/DRF и клиентской частью на Vue 3 + Pinia.

![Скриншот приложения (заглушка)](docs/images/screenshot-placeholder.png)

## Стек технологий

- **Backend:** Django 5, Django REST Framework
- **Frontend:** Vue.js 3, Pinia, Vite
- **База данных:** SQLite
- **Язык:** Python 3.12+, JavaScript (ES2022+)

## Системные требования

- Python **3.12+**
- Node.js **20+**
- npm **10+**
- Git

## Установка и запуск

### 1) Клонирование репозитория

```bash
git clone <repo_url>
cd <repo_name>
```

---

### 2) Бэкенд (Django + DRF)

#### Шаг 1. Создайте виртуальное окружение

```bash
python -m venv .venv
```

#### Шаг 2. Активируйте виртуальное окружение

**macOS / Linux:**

```bash
source .venv/bin/activate
```

**Windows (PowerShell):**

```powershell
.venv\Scripts\Activate.ps1
```

#### Шаг 3. Установите зависимости

```bash
pip install -r requirements.txt
```

#### Шаг 4. Выполните миграции

```bash
python manage.py migrate
```

#### Шаг 5. Создайте суперпользователя (опционально)

```bash
python manage.py createsuperuser
```

#### Шаг 6. Запустите бэкенд-сервер

```bash
python manage.py runserver
```

Бэкенд будет доступен по адресу: `http://127.0.0.1:8000`

---

### 3) Фронтенд (Vue.js 3 + Pinia)

> Ниже предполагается, что фронтенд находится в директории `frontend/`.

#### Шаг 1. Перейдите в директорию фронтенда

```bash
cd frontend
```

#### Шаг 2. Установите зависимости

```bash
npm install
```

#### Шаг 3. Запустите dev-сервер

```bash
npm run dev
```

Фронтенд будет доступен по адресу (обычно): `http://127.0.0.1:5173`

## Демо-учётные данные

Используйте тестового пользователя:

- **Логин:** `demo`
- **Пароль:** `demo1234`

> Рекомендуется сменить или отключить демо-аккаунт в production.

## Структура проекта

```text
.
├── backend/
│   ├── manage.py
│   ├── config/
│   ├── apps/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
├── docs/
│   └── images/
│       └── screenshot-placeholder.png
└── README.md
```

## API Endpoints

| Метод | Endpoint              | Описание                          |
|------:|-----------------------|-----------------------------------|
| GET   | `/api/health/`        | Проверка доступности API          |
| POST  | `/api/auth/login/`    | Авторизация пользователя          |
| POST  | `/api/auth/logout/`   | Выход пользователя                |
| GET   | `/api/tasks/`         | Получение списка задач            |
| POST  | `/api/tasks/`         | Создание новой задачи             |
| GET   | `/api/tasks/{id}/`    | Получение задачи по ID            |
| PATCH | `/api/tasks/{id}/`    | Частичное обновление задачи       |
| DELETE| `/api/tasks/{id}/`    | Удаление задачи                   |

## Запуск тестов

### Бэкенд

```bash
python manage.py test
```

### Фронтенд

```bash
cd frontend
npm run test
```

## Автор

- Ваше имя
- Email: `you@example.com`
- GitHub: [@your-username](https://github.com/your-username)
