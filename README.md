# Foodgram

Foodgram - сервис для публикации рецептов. Пользователи могут создавать рецепты, подписываться на авторов, добавлять рецепты в избранное и список покупок, а также скачивать список ингредиентов для выбранных блюд.

## Ссылки

- Сайт: https://zxczxc.servequake.com/
- Админка: https://zxczxc.servequake.com/admin/
- Документация API: https://zxczxc.servequake.com/api/docs/
- Пример рецепта 1: https://zxczxc.servequake.com/recipes/1
- Пример рецепта 2: https://zxczxc.servequake.com/recipes/2

## Возможности

- Регистрация, вход, выход и смена пароля.
- Просмотр рецептов, страниц авторов и отдельных рецептов.
- Создание, редактирование и удаление своих рецептов.
- Фильтрация рецептов по тегам.
- Подписки на авторов.
- Добавление рецептов в избранное.
- Добавление рецептов в список покупок.
- Скачивание списка покупок с суммированием одинаковых ингредиентов.
- Админ-зона для управления пользователями, рецептами, тегами и ингредиентами.

## Технологии

- Python 3.11
- Django 4.2
- Django REST Framework
- PostgreSQL
- Gunicorn
- Nginx
- Docker, Docker Compose
- React

## Локальный запуск в Docker

1. Перейдите в папку проекта:

```bash
cd foodgram-main
```

2. Создайте файл окружения `infra/.env`:

```env
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram
POSTGRES_PASSWORD=foodgram
DB_HOST=db
DB_PORT=5432
SECRET_KEY=foodgram-local-secret-key
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=admin
```

3. Соберите фронтенд:

```bash
cd infra
docker compose build frontend
docker compose run --rm frontend
```

4. Запустите проект:

```bash
docker compose up -d
```

Backend применит миграции, загрузит ингредиенты из `data/ingredients.json`, создаст тестовые данные и соберет статику.

После запуска проект будет доступен:

- сайт: http://localhost/
- админка: http://localhost/admin/
- документация API: http://localhost/api/docs/

## Примеры API-запросов

Получить список рецептов:

```http
GET /api/recipes/
```

Получить отдельный рецепт:

```http
GET /api/recipes/1/
```

Получить список тегов:

```http
GET /api/tags/
```

Добавить рецепт в список покупок:

```http
POST /api/recipes/1/shopping_cart/
Authorization: Token <token>
```

Скачать список покупок:

```http
GET /api/recipes/download_shopping_cart/
Authorization: Token <token>
```

## Деплой

Проект развернут на удаленном сервере в трех контейнерах:

- `nginx` - проксирование запросов, HTTPS, раздача статики и медиафайлов;
- `db` - база данных PostgreSQL;
- `backend` - Django-приложение с Gunicorn.

Backend-образ опубликован в Docker Hub:

```text
zxcuwuu/foodgram_backend:latest
```

## Доступы для ревью

```yaml
login: admin@example.com
password: admin
vm_name: r-backend-vm-897965943
```

## Автор

Zxcuwuu
