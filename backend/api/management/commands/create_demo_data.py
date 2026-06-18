import base64
import os

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from api.models import Ingredient, Recipe, RecipeIngredient, Tag, User


SAMPLE_IMAGE = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD"
    "///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNo"
    "AAAAggCByxOyYQAAAABJRU5ErkJggg=="
)


class Command(BaseCommand):
    help = "Create superuser, demo users and demo recipes."

    def handle(self, *args, **options):
        self.create_superuser()
        users = self.create_users()
        self.create_recipes(users)
        self.stdout.write(self.style.SUCCESS("Demo data ready."))

    def create_superuser(self):
        username = os.getenv("DJANGO_SUPERUSER_USERNAME", "admin")
        email = os.getenv("DJANGO_SUPERUSER_EMAIL", "admin@example.com")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD")
        if not password:
            return
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "username": username,
                "first_name": "Admin",
                "last_name": "Foodgram",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            user.set_password(password)
            user.save()

    def create_users(self):
        demo_users = [
            {
                "email": "chef@example.com",
                "username": "chef",
                "first_name": "Анна",
                "last_name": "Поварова",
                "password": "demo-password",
            },
            {
                "email": "taster@example.com",
                "username": "taster",
                "first_name": "Илья",
                "last_name": "Дегустатор",
                "password": "demo-password",
            },
        ]
        users = []
        for data in demo_users:
            password = data.pop("password")
            user, created = User.objects.get_or_create(
                email=data["email"],
                defaults=data,
            )
            if created:
                user.set_password(password)
                user.save()
            users.append(user)
        return users

    def create_recipes(self, users):
        if not Ingredient.objects.exists() or not Tag.objects.exists():
            return
        ingredients = list(Ingredient.objects.all()[:3])
        tags = list(Tag.objects.all()[:3])
        recipes = [
            {
                "author": users[0],
                "name": "Быстрый завтрак",
                "text": "Смешайте ингредиенты и подавайте сразу.",
                "cooking_time": 5,
                "tags": tags[:1],
                "ingredients": ingredients[:2],
            },
            {
                "author": users[1],
                "name": "Домашний обед",
                "text": "Готовьте на среднем огне до готовности.",
                "cooking_time": 25,
                "tags": tags[1:2] or tags[:1],
                "ingredients": ingredients[1:3] or ingredients[:1],
            },
        ]
        for data in recipes:
            image_content = ContentFile(
                base64.b64decode(SAMPLE_IMAGE),
                name=f"{data['name']}.png",
            )
            recipe, created = Recipe.objects.get_or_create(
                name=data["name"],
                author=data["author"],
                defaults={
                    "text": data["text"],
                    "cooking_time": data["cooking_time"],
                    "image": image_content,
                },
            )
            if not created:
                continue
            recipe.tags.set(data["tags"])
            RecipeIngredient.objects.bulk_create(
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient,
                    amount=100 + index * 50,
                )
                for index, ingredient in enumerate(data["ingredients"])
            )
