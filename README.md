┌─────────────────────────────────────────────────────────────────┐
│                     КЛИЕНТСКАЯ ЧАСТЬ                             │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              Flutter Desktop Application                   │ │
│  │              (Windows, macOS, Linux)                       │ │
│  └─────────────────────┬─────────────────────────────────────┘ │
└────────────────────────┼─────────────────────────────────────────┘
                         │ HTTPS
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     СЕРВЕРНАЯ ЧАСТЬ (Backend)                    │
│                                                                   │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                      API Layer                             │ │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐      │ │
│  │  │  /auth/*     │ │  /users/*    │ │ /apartments/*│      │ │
│  │  │  регистрация │ │  профиль     │ │   квартиры   │      │ │
│  │  │  вход        │ │              │ │              │      │ │
│  │  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘      │ │
│  └─────────┼────────────────┼────────────────┼───────────────┘ │
│            ▼                ▼                ▼                  │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                  Service Layer                            │ │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐      │ │
│  │  │ AuthService  │ │ UserService  │ │ ApartmentSvc │      │ │
│  │  │ - регистрация│ │ - профиль    │ │ - CRUD       │      │ │
│  │  │ - логика     │ │ - валидация  │ │ - бизнес-лог │      │ │
│  │  └──────────────┘ └──────────────┘ └──────────────┘      │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                    Data Layer                              │ │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐      │ │
│  │  │   Models     │ │  Repositories│ │   Database    │      │ │
│  │  │  (SQLAlchemy)│ │  (CRUD)      │ │  PostgreSQL   │      │ │
│  │  └──────────────┘ └──────────────┘ └──────┬───────┘      │ │
│  └────────────────────────────────────────────┼────────────────┘ │
│                                               │                   │
│  ┌────────────────────────────────────────────┼────────────────┐ │
│  │              Core Layer                    │                │ │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────▼───────┐      │ │
│  │  │   Config     │ │   Security   │ │   Database    │      │ │
│  │  │  (.env)      │ │  (JWT, хеш)  │ │  Connection   │      │ │
│  │  └──────────────┘ └──────────────┘ └──────────────┘      │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘


🧩 Компоненты системы
1. API Layer (Слой представления)
Расположение: app/api/v1/endpoints/

Назначение: Точки входа HTTP-запросов

Компоненты:

auth.py — эндпоинты авторизации

users.py — эндпоинты пользователей

apartments.py — эндпоинты квартир

Ответственность: Валидация входящих данных, вызов сервисов, формирование ответов

2. Service Layer (Слой бизнес-логики)
Расположение: app/services/

Назначение: Реализация бизнес-правил

Компоненты:

auth_service.py — регистрация, вход, токены

apartment_service.py — работа с квартирами

Ответственность: Проверка прав, выполнение операций, координация вызовов

3. Data Layer (Слой данных)
Расположение: app/models/, app/repositories/

Назначение: Работа с базой данных

Компоненты:

models/ — SQLAlchemy модели (структура таблиц)

repositories/ — паттерн Repository (CRUD операции)

Ответственность: Сохранение, извлечение, обновление данных

4. Core Layer (Ядро)
Расположение: app/core/

Назначение: Базовые сервисы и настройки

Компоненты:

config.py — конфигурация из .env

database.py — подключение к PostgreSQL

security.py — хеширование, JWT

Ответственность: Инфраструктура, общие утилиты

5. Schema Layer (Схемы)
Расположение: app/schemas/

Назначение: Pydantic модели для валидации

Компоненты:

user.py — схемы пользователя (Create, Login, Response)

apartment.py — схемы квартиры

Ответственность: Валидация ввода/вывода, документация API




arthouse-backend/
│
├── app/                                      # Основной пакет приложения
│   │
│   ├── main.py                               # Точка входа FastAPI
│   │   ├── create_app()                       # Инициализация приложения
│   │   ├── include_routers()                   # Подключение эндпоинтов
│   │   └── configure_middleware()               # CORS и middleware
│   │
│   ├── core/                                   # Ядро системы
│   │   ├── config.py                            # Pydantic Settings
│   │   │   ├── DatabaseSettings                  # Настройки БД
│   │   │   ├── SecuritySettings                   # JWT, секреты
│   │   │   └── AppSettings                         # Общие настройки
│   │   │
│   │   ├── database.py                           # Подключение к БД
│   │   │   ├── engine                              # SQLAlchemy engine
│   │   │   ├── SessionLocal                         # Фабрика сессий
│   │   │   └── get_db()                              # Dependency для FastAPI
│   │   │
│   │   └── security.py                            # Безопасность
│   │       ├── hash_password()                      # bcrypt хеширование
│   │       ├── verify_password()                     # Проверка пароля
│   │       ├── create_access_token()                  # Генерация JWT
│   │       ├── verify_token()                          # Проверка JWT
│   │       └── get_current_user()                      # Dependency для защиты
│   │
│   ├── models/                                   # SQLAlchemy модели
│   │   ├── __init__.py                            # Связывание моделей
│   │   ├── user.py                                 # Модель пользователя
│   │   │   ├── id                                   # Primary key
│   │   │   ├── email                                 # Уникальный email
│   │   │   ├── username                                # Имя
│   │   │   ├── password_hash                            # Хеш пароля
│   │   │   ├── is_active                                 # Статус
│   │   │   ├── created_at                                 # Дата регистрации
│   │   │   └── updated_at                                 # Дата обновления
│   │   │
│   │   └── apartment.py                            # Модель квартиры
│   │       ├── id                                    # Primary key
│   │       ├── user_id                                 # Foreign key to users
│   │       ├── name                                      # Название
│   │       ├── ceiling_height                             # Высота потолков
│   │       ├── square_meters                                # Площадь
│   │       ├── floors                                        # Этажи
│   │       ├── rooms_count                                    # Комнаты
│   │       ├── address                                         # Адрес
│   │       ├── created_at                                       # Дата создания
│   │       └── updated_at                                       # Дата обновления
│   │
│   ├── schemas/                                   # Pydantic схемы
│   │   ├── __init__.py                            # Экспорт схем
│   │   ├── user.py                                 # Схемы пользователя
│   │   │   ├── UserCreate                            # Вход: регистрация
│   │   │   ├── UserLogin                              # Вход: логин
│   │   │   ├── UserResponse                             # Выход: данные
│   │   │   └── Token                                     # Выход: JWT
│   │   │
│   │   └── apartment.py                            # Схемы квартиры
│   │       ├── ApartmentCreate                        # Вход: создание
│   │       ├── ApartmentUpdate                          # Вход: обновление
│   │       └── ApartmentResponse                          # Выход: данные
│   │
│   ├── services/                                  # Бизнес-логика
│   │   ├── __init__.py
│   │   ├── auth_service.py                          # Сервис авторизации
│   │   │   ├── register()                              # Регистрация
│   │   │   │   ├── check_email_exists()                  # Проверка email
│   │   │   │   ├── hash_password()                         # Хеширование
│   │   │   │   ├── save_user()                               # Сохранение
│   │   │   │   └── generate_token()                           # Токен
│   │   │   │
│   │   │   └── login()                                 # Вход
│   │   │       ├── find_user()                            # Поиск
│   │   │       ├── verify_password()                        # Проверка
│   │   │       └── generate_token()                           # Токен
│   │   │
│   │   └── apartment_service.py                      # Сервис квартир
│   │       ├── get_user_apartment()                      # Получение
│   │       ├── create_apartment()                          # Создание
│   │       └── update_apartment()                            # Обновление
│   │
│   └── api/                                       # API слой
│       ├── __init__.py
│       └── v1/                                      # Версия 1
│           ├── __init__.py
│           ├── api.py                                 # Сборка роутеров
│           │   └── router = APIRouter()                 # Главный роутер
│           │       ├── include(auth.router)
│           │       ├── include(users.router)
│           │       └── include(apartments.router)
│           │
│           └── endpoints/                            # Эндпоинты
│               ├── __init__.py
│               ├── auth.py                              # /auth/*
│               │   ├── POST /register                     # Регистрация
│               │   └── POST /login                          # Вход
│               │
│               ├── users.py                              # /users/*
│               │   └── GET /me                              # Профиль
│               │
│               └── apartments.py                         # /apartments/*
│                   ├── GET /my                               # Моя квартира
│                   └── POST /my                               # Создать/обновить
│
├── .env                                          # Переменные окружения
├── .env.example                                   # Пример .env
├── requirements.txt                               # Зависимости
├── init_db.py                                     # Скрипт инициализации БД
├── test_db.py                                      # Проверка подключения
└── README.md                                       # Документация
--------------------------------------------------------------------------------------------

[Клиент (Flutter)]
    │
    │ POST /api/v1/auth/register
    │ {"email": "...", "username": "...", "password": "..."}
    ▼
[API Layer - auth.py]
    │
    │ 1. Принять запрос
    │ 2. Валидация через UserCreate (schema)
    │ 3. Вызвать AuthService.register()
    ▼
[Service Layer - auth_service.py]
    │
    │ 1. Проверить email в БД (models)
    │ 2. Захешировать пароль (core/security.py)
    │ 3. Создать пользователя (models)
    │ 4. Сгенерировать JWT (core/security.py)
    ▼
[Data Layer - models]
    │
    │ 1. Сохранить в PostgreSQL (database.py)
    │ 2. Вернуть созданного пользователя
    ▼
[Service Layer]
    │
    │ Вернуть токен и данные
    ▼
[API Layer]
    │
    │ Сериализовать ответ через Token (schema)
    ▼
[Клиент]
    │
    │ {"access_token": "...", "token_type": "bearer"}

    Отличная идея! Вот полная инструкция для команды, как запустить проект. Сохрани это как `README.md` в корне проекта или отправь ссылку на этот файл.

---

# 🏠 ARThouse Backend - Инструкция по запуску

## 📋 Содержание
1. [Требования](#требования)
2. [Быстрый старт за 5 минут](#быстрый-старт-за-5-минут)
3. [Подробная инструкция](#подробная-инструкция)
4. [Структура проекта](#структура-проекта)
5. [API и тестирование](#api-и-тестирование)
6. [Частые проблемы и решения](#частые-проблемы-и-решения)

---

## ⚡ Требования

| Компонент | Версия | Где взять |
|-----------|--------|-----------|
| **Python** | 3.11+ | [python.org](https://www.python.org/downloads/) |
| **PostgreSQL** | 15+ | [postgresql.org](https://www.postgresql.org/download/windows/) |
| **Git** | любая | [git-scm.com](https://git-scm.com/download/win) |
| **ОС** | Windows/Mac/Linux | - |

---

## 🚀 Быстрый старт за 5 минут

### 1. Клонируем проект
```bash
git clone <ссылка_на_репозиторий>
cd arthouse-backend
```

### 2. Настраиваем базу данных
```bash
# Заходим в PostgreSQL
psql -U postgres

# Создаём базу (прямо в psql)
CREATE DATABASE arthouse_db;
\q
```

### 3. Запускаем одной командой (Windows)
```powershell
# Просто скопируй и вставь это в PowerShell:
python -m venv venv && .\venv\Scripts\activate && pip install -r requirements.txt && python init_db.py && python run.py
```

### 4. Открываем в браузере
```
http://127.0.0.1:8000/docs
```

---

## 📚 Подробная инструкция

### Шаг 1: Установка Python и PostgreSQL

#### Windows 🪟
1. Скачай Python с [официального сайта](https://www.python.org/downloads/)
2. При установке **обязательно** отметь галочку "Add Python to PATH"
3. Скачай PostgreSQL с [официального сайта](https://www.postgresql.org/download/windows/)
4. Запомни пароль, который вводишь при установке!

#### Mac 🍎
```bash
# Установка Python
brew install python@3.11

# Установка PostgreSQL
brew install postgresql@15
brew services start postgresql@15
```

#### Linux 🐧
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3-pip postgresql postgresql-contrib
sudo systemctl start postgresql
```

### Шаг 2: Клонирование и подготовка

```bash
# Клонируем проект
git clone <ссылка_на_репозиторий>
cd arthouse-backend

# Создаём виртуальное окружение
python -m venv venv

# Активируем его:
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Устанавливаем зависимости
pip install -r requirements.txt
```

### Шаг 3: Настройка PostgreSQL

#### Способ 1: Через командную строку
```bash
# Заходим в PostgreSQL
psql -U postgres

# Внутри psql выполняем:
CREATE DATABASE arthouse_db;
\q
```

#### Способ 2: Через pgAdmin (графический интерфейс)
1. Открой pgAdmin
2. Нажми правой кнопкой на "Databases" → "Create" → "Database"
3. Введи имя: `arthouse_db`
4. Нажми "Save"

### Шаг 4: Создаём файл .env

Скопируй `.env.example` в `.env` и отредактируй:

```env
# Настройки приложения
APP_NAME=ARThouse API
APP_VERSION=0.1.0
DEBUG=True

# Настройки сервера
HOST=127.0.0.1
PORT=8000

# Настройки базы данных
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=           # Оставь пустым, если нет пароля
POSTGRES_DB=arthouse_db
POSTGRES_PORT=5432

# Настройки безопасности
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Шаг 5: Инициализация и запуск

```bash
# Создаём таблицы в БД
python init_db.py

# Проверяем подключение
python test_db.py

# Запускаем сервер!
python run.py
```

### Шаг 6: Проверка

Открой браузер и перейди по адресу:
```
http://127.0.0.1:8000/docs
```

Ты должна увидеть Swagger UI с документацией API! 🎉

---

## 📁 Структура проекта (что где лежит)

```
arthouse-backend/
│
├── app/                    # Основной код приложения
│   ├── api/               # Эндпоинты (точки входа)
│   │   └── v1/           
│   │       ├── endpoints/ # Auth, Users, Apartments
│   │       └── api.py     # Сборка всех роутеров
│   │
│   ├── core/              # Ядро (config, database, security)
│   ├── models/            # Модели БД (User, Apartment)
│   ├── schemas/           # Pydantic схемы (валидация)
│   ├── services/          # Бизнес-логика
│   └── repositories/      # Работа с БД (CRUD)
│
├── .env                   # Твои настройки (не в git)
├── .env.example           # Пример настроек
├── requirements.txt       # Зависимости Python
├── init_db.py            # Скрипт создания таблиц
├── test_db.py            # Проверка БД
└── run.py                # Запуск сервера
```

---

## 🔌 API Endpoints (что умеет бэкенд)

| Метод | URL | Описание | Нужен токен? |
|-------|-----|----------|--------------|
| POST | `/api/v1/auth/register` | Регистрация | ❌ |
| POST | `/api/v1/auth/login` | Вход | ❌ |
| GET | `/api/v1/users/me` | Мой профиль | ✅ |
| GET | `/api/v1/apartments/my` | Мои квартиры | ✅ |
| POST | `/api/v1/apartments/my` | Создать квартиру | ✅ |
| GET | `/api/v1/apartments/my/{id}` | Квартира по ID | ✅ |
| PUT | `/api/v1/apartments/my/{id}` | Обновить квартиру | ✅ |
| DELETE | `/api/v1/apartments/my/{id}` | Удалить квартиру | ✅ |

---

## 🧪 Тестирование API через Swagger

1. Запусти сервер: `python run.py`
2. Открой `http://127.0.0.1:8000/docs`
3. **Тест регистрации:**
   - Найди `POST /api/v1/auth/register`
   - Нажми "Try it out"
   - Введи:
     ```json
     {
       "email": "test@test.com",
       "username": "testuser",
       "password": "123456"
     }
     ```
   - Нажми "Execute"
   - Скопируй `access_token` из ответа

4. **Авторизация:**
   - Нажми кнопку "Authorize" (🔓 вверху справа)
   - Введи: `Bearer ТВОЙ_ТОКЕН`
   - Нажми "Authorize"

5. **Создание квартиры:**
   - Найди `POST /api/v1/apartments/my`
   - Введи:
     ```json
     {
       "name": "Моя квартира",
       "ceiling_height": 2.7,
       "square_meters": 54.3,
       "floors": 1,
       "rooms_count": 2,
       "address": "Москва, ул. Ленина, д. 1"
     }
     ```

---

## 🔧 Устранение проблем (что делать если...)

### ❌ "psql не найдена"
```powershell
# Найди, где установлен PostgreSQL:
dir "C:\Program Files\PostgreSQL\"
# Или добавь в PATH:
$env:Path += ";C:\Program Files\PostgreSQL\15\bin"
```

### ❌ "password authentication failed"
```env
# В .env просто оставь пароль пустым:
POSTGRES_PASSWORD=
```

### ❌ "database does not exist"
```powershell
# Создай базу заново:
psql -U postgres -c "CREATE DATABASE arthouse_db;"
```

### ❌ "port already in use"
```powershell
# Найди процесс на порту 8000:
netstat -ano | findstr :8000
# Убей процесс (замени PID на свой):
taskkill /PID 12345 /F
```

### ❌ "ModuleNotFoundError"
```bash
# Переустанови все зависимости:
pip install -r requirements.txt --force-reinstall
```

### ❌ "Документация не открывается"
Проверь в `.env`:
```env
DEBUG=True  # Должно быть True
```

### ❌ "Всё сломалось, хочу начать заново"
```powershell
# Удали БД и создай заново:
psql -U postgres -c "DROP DATABASE IF EXISTS arthouse_db;"
psql -U postgres -c "CREATE DATABASE arthouse_db;"
python init_db.py
python run.py
```

---

## 💡 Полезные команды (шпаргалка)

```powershell
# Активировать окружение (Windows)
.\venv\Scripts\activate

# Активировать окружение (Mac/Linux)
source venv/bin/activate

# Установить всё с нуля
pip install -r requirements.txt

# Запустить сервер
python run.py

# Пересоздать БД
python init_db.py

# Проверить БД
python test_db.py

# Войти в PostgreSQL
psql -U postgres -d arthouse_db

# Посмотреть таблицы в БД
psql -U postgres -d arthouse_db -c "\dt"
```

---

## 🏃‍♀️ Самые быстрые команды (копируй и вставляй)

### Windows PowerShell (одной строкой):
```powershell
python -m venv venv; .\venv\Scripts\activate; pip install -r requirements.txt; python init_db.py; python run.py
```

### Mac/Linux:
```bash
python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt && python init_db.py && python run.py
```

---

## 📞 Если ничего не помогает

1. **Проверь логи** - они обычно пишут, в чём проблема
2. **Перезапусти всё** - компьютер, PostgreSQL, сервер
3. **Создай issue** в репозитории проекта
4. **Напиши в чат команды** - вместе разберёмся!

---

## 🎉 Поздравляю!

Если ты видишь это сообщение в терминале:
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

А в браузере открывается http://127.0.0.1:8000/docs

**ТЫ ВСЁ СДЕЛАЛА ПРАВИЛЬНО!** 🚀
