# Foodgram

Foodgram — веб-приложение для публикации рецептов. Пользователи могут создавать рецепты, подписываться на авторов, добавлять рецепты в избранное и список покупок, а затем скачивать итоговый список ингредиентов.

## Технологии

- Python 3.11
- Django 4.2
- Django REST Framework
- PostgreSQL
- Docker, Docker Compose
- Gunicorn
- Nginx
- React

## Возможности

- Регистрация и авторизация пользователей по токену.
- Создание, редактирование и удаление рецептов.
- Фильтрация рецептов по тегам, автору, избранному и списку покупок.
- Подписки на авторов.
- Избранные рецепты.
- Список покупок с суммированием ингредиентов.
- Загрузка и удаление аватара пользователя.
- Админ-зона Django.

## Запуск проекта

1. Клонируйте репозиторий:

```bash
git clone https://github.com/Zxcuwuu/foodgram.git
cd foodgram
```

2. Создайте файл окружения:

```bash
cp infra/.env.example infra/.env
```

Пример переменных окружения:

```env
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram
POSTGRES_PASSWORD=foodgram
DB_HOST=db
DB_PORT=5432
SECRET_KEY=replace-me
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=admin
```

3. Запустите контейнеры:

```bash
cd infra
docker compose up --build -d
```

При запуске backend применит миграции, загрузит ингредиенты из `data/ingredients.json`, создаст демо-данные и соберёт статику.

4. Откройте проект:

- Сайт: http://localhost/
- Документация API: http://localhost/api/docs/
- Админ-зона: http://localhost/admin/

Демо-администратор создаётся из переменных `DJANGO_SUPERUSER_USERNAME` и `DJANGO_SUPERUSER_PASSWORD`.

## Полезные команды

Остановить проект:

```bash
docker compose down
```

Посмотреть логи backend:

```bash
docker logs foodgram-backend
```

Применить миграции вручную:

```bash
docker compose exec backend python manage.py migrate
```

Загрузить ингредиенты вручную:

```bash
docker compose exec backend python manage.py load_ingredients
```

## Примеры запросов API

Регистрация пользователя:

```http
POST /api/users/
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "user",
  "first_name": "Иван",
  "last_name": "Иванов",
  "password": "strong-password"
}
```

Получение токена:

```http
POST /api/auth/token/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "strong-password"
}
```

Получение списка рецептов:

```http
GET /api/recipes/?page=1&limit=6&tags=breakfast
```

Создание рецепта:

```http
POST /api/recipes/
Authorization: Token <token>
Content-Type: application/json

{
  "ingredients": [
    {
      "id": 1,
      "amount": 100
    }
  ],
  "tags": [1],
  "image": "data:image/png;base64,...",
  "name": "Завтрак",
  "text": "Описание рецепта",
  "cooking_time": 10
}
```

Добавление рецепта в список покупок:

```http
POST /api/recipes/1/shopping_cart/
Authorization: Token <token>
```

Скачивание списка покупок:

```http
GET /api/recipes/download_shopping_cart/
Authorization: Token <token>
```

## Автор

Zxcuwuu  
GitHub: https://github.com/Zxcuwuu
