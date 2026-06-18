Foodgram — сервис для публикации рецептов, подписок на авторов, избранного и списка покупок.

## Локальный запуск в Docker

1. Создайте файл окружения:

```bash
cp infra/.env.example infra/.env
```

2. Запустите проект:

```bash
cd infra
docker-compose up --build
```

Backend применит миграции, загрузит ингредиенты из `data/ingredients.json` и соберёт статику.

Фронтенд будет доступен на http://localhost, документация API — на http://localhost/api/docs/.

