URL Shortener Service
Сервис для сокращения ссылок с возможностью создания кастомных алиасов, статистикой переходов и управлением через API.

Возможности
Обязательный функционал:
 * Создание короткой ссылки — POST /links/shorten
 * Редирект на оригинальный URL — GET /links/{short_code}
 * Удаление ссылки — DELETE /links/{short_code}
 * Обновление ссылки — PUT /links/{short_code}
 * Статистика по ссылке — GET /links/{short_code}/stats
 * Кастомные алиасы — возможность задать свой короткий код
 * Поиск по оригинальному URL — GET /links/search?original_url={url}
 * Время жизни ссылки — параметр expires_at при создании

Дополнительные функции:
* Регистрация и авторизация пользователей (JWT)
* Разграничение прав — изменение/удаление только для владельцев
* Кэширование популярных ссылок (Redis)
* Автоматическая очистка истекших ссылок
* Статистика переходов — количество кликов, дата последнего использования
* Docker-контейнеризация — лёгкий запуск одной командой

 Технологический стек
Компонент	                    Технология
Web-фреймворк	                 FastAPI
База данных	                   PostgreSQL
Кэширование	                     Redis
Аутентификация	            JWT (python-jose)
Хеширование паролей	        passlib + bcrypt
ORM	                           SQLAlchemy
Валидация	                    Pydantic
Контейнеризация	          Docker + Docker Compose

Запуск через Docker: 

1. Клонировать репозиторий
git clone https://github.com/vasilisadan18/url-shortener.git
cd url-shortener

2. Запустить с Docker Compose
docker-compose up -d

Сервис будет доступен по адресу: http://localhost:8000

Локальный запуск:

1. Установить зависимости
pip install -r requirements.txt

2. Настроить переменные окружения
cp .env.example .env

3. Запустить сервис
uvicorn app.main:app --reload


API Документация
После запуска документация доступна по адресам:

Swagger UI: http://localhost:8000/docs

ReDoc: http://localhost:8000/redoc

Примеры запросов
1. Создание короткой ссылки
* Простая ссылка (автоматическая генерация кода)
bash
curl -X POST "http://localhost:8000/api/v1/links/shorten" \
  -H "Content-Type: application/json" \
  -d '{
    "original_url": "https://www.google.com"
  }'

Ответ:
json
{
  "id": "db3c1949-2d05-4f64-8578-e6a8bcfb2f59",
  "short_code": "2LfSSW",
  "original_url": "https://www.google.com/",
  "short_url": "http://localhost:8000/2LfSSW",
  "custom_alias": null,
  "clicks": 0,
  "created_at": "2026-03-08T15:26:45.780168Z",
  "expires_at": null,
  "is_active": true
}

* С кастомным алиасом
bash
curl -X POST "http://localhost:8000/api/v1/links/shorten" \
  -H "Content-Type: application/json" \
  -d '{
    "original_url": "https://www.github.com",
    "custom_alias": "github"
  }'

Ответ:
json
{
  "id": "036b9830-eeb2-4faa-98af-5bb2d037def7",
  "short_code": "github",
  "original_url": "https://www.github.com/",
  "short_url": "http://localhost:8000/github",
  "custom_alias": "github",
  "clicks": 0,
  "created_at": "2026-03-08T15:26:58.468149Z",
  "expires_at": null,
  "is_active": true
}

* С указанием времени жизни
bash
curl -X POST "http://localhost:8000/api/v1/links/shorten" \
  -H "Content-Type: application/json" \
  -d '{
    "original_url": "https://www.example.com",
    "custom_alias": "temp-link",
    "expires_at": "2025-12-31T23:59:59"
  }'

2. Редирект по короткой ссылке
* Через API
bash
curl -L http://localhost:8000/api/v1/links/github -v

* Через корневой путь
bash
curl -L http://localhost:8000/github -v
Результат: 307 Temporary Redirect на https://www.github.com/

3. Получение статистики

bash
curl http://localhost:8000/api/v1/links/github/stats

Ответ:
json
{
  "id": "036b9830-eeb2-4faa-98af-5bb2d037def7",
  "short_code": "github",
  "original_url": "https://www.github.com/",
  "short_url": "http://localhost:8000/github",
  "custom_alias": "github",
  "clicks": 1,
  "created_at": "2026-03-08T15:26:58.468149Z",
  "expires_at": null,
  "is_active": true,
  "last_accessed_at": "2026-03-08T15:30:00.000000Z",
  "days_until_expiry": null
}

4. Регистрация пользователя
bash
curl -X POST "http://localhost:8000/api/v1/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "password123"
  }'

Ответ:
json
{
  "email": "user@example.com",
  "username": "testuser",
  "id": "fa93c422-b4f8-4241-ba9e-9954707fb5e7",
  "is_active": true
}

5. Авторизация (получение JWT токена)
bash
curl -X POST "http://localhost:8000/api/v1/users/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'

Ответ:
json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}

Сохраните токен:

bash
export TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

6. Создание ссылки от имени пользователя

bash
curl -X POST "http://localhost:8000/api/v1/links/shorten" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "original_url": "https://www.google.com",
    "custom_alias": "my-private-link"
  }'

7. Обновление ссылки

bash
curl -X PUT "http://localhost:8000/api/v1/links/my-private-link" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "original_url": "https://www.google.com/search"
  }'

8. Удаление ссылки

bash
curl -X DELETE "http://localhost:8000/api/v1/links/my-private-link" \
  -H "Authorization: Bearer $TOKEN"

9. Поиск по оригинальному URL
bash
curl "http://localhost:8000/api/v1/links/search?original_url=google.com"
Ответ: (массив найденных ссылок)
json
[
  {
    "short_code": "2LfSSW",
    "short_url": "http://localhost:8000/2LfSSW",
    "original_url": "https://www.google.com/",
    "created_at": "2026-03-08T15:26:45.780168Z",
    "clicks": 3
  },
  {
    "short_code": "my-private-link",
    "short_url": "http://localhost:8000/my-private-link",
    "original_url": "https://www.google.com/search",
    "created_at": "2026-03-08T15:35:00.000000Z",
    "clicks": 0
  }
]


Структура базы данных
Таблица users
Поле	                  Тип	                  Описание
id	                      UUID	                 Первичный ключ
email	                  String	             Уникальный email
username	              String	             Уникальное имя пользователя
hashed_password	          String	             Хеш пароля
is_active	              Boolean	             Активен ли пользователь
created_at	              Timestamp	             Дата регистрации

Таблица links
Поле	                  Тип	                  Описание
id	                      UUID	                  Первичный ключ
short_code	              String	              Уникальный короткий код
original_url	          String	              Оригинальный URL
custom_alias	          String	              Кастомный алиас (опционально)
clicks	                  Integer	              Количество переходов
created_at	              Timestamp		          Дата создания
updated_at	              Timestamp		          Дата последнего обновления
last_accessed_at	      Timestamp			      Дата последнего перехода
expires_at	              Timestamp			      Дата истечения (опционально)
is_active	              Boolean			      Активна ли ссылка
user_id	                  UUID			          Внешний ключ к users

Кэширование (Redis)
- Популярные ссылки кэшируются на 1 час
- При обновлении или удалении ссылки кэш автоматически очищается
- Статистика переходов всегда актуальна (записывается в БД)

Docker Compose
Запуск одной командой:     docker-compose up -d

Тестирование и покрытие кода

Результаты тестирования
![alt text](<Снимок экрана (270).png>)

Запуск тестов:

1. Установка зависимостей
pip install -r tests/requirements-test.txt

2. Запуск всех тестов
pytest -v

3. Проверка покрытия
coverage run -m pytest
coverage report
coverage html