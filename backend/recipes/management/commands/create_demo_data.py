from io import BytesIO
import os

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from PIL import Image, ImageDraw, ImageFont

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.models import User


IMAGE_SIZE = (900, 520)
IMAGE_COLORS = (
    ("#f7c873", "#d86c4a"),
    ("#9dd7c6", "#2f7f78"),
    ("#f1a7a1", "#a84b5f"),
    ("#c4d87f", "#5f8f47"),
    ("#b8c9ff", "#4d66aa"),
    ("#ffd1dc", "#b6577a"),
    ("#ffdd8f", "#9a5f28"),
    ("#c7ead9", "#4c927a"),
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
            {
                "author": users[0],
                "name": "Вечерний салат",
                "text": "Нарежьте ингредиенты и аккуратно перемешайте.",
                "cooking_time": 15,
                "tags": tags[2:3] or tags[:1],
                "ingredients": ingredients[:3],
            },
            {
                "author": users[1],
                "name": "Сытная закуска",
                "text": "Подавайте сразу после приготовления.",
                "cooking_time": 12,
                "tags": tags[:2],
                "ingredients": ingredients[:2],
            },
            {
                "author": users[0],
                "name": "Лёгкий суп",
                "text": "Варите до мягкости ингредиентов.",
                "cooking_time": 30,
                "tags": tags[1:2] or tags[:1],
                "ingredients": ingredients[1:3] or ingredients[:1],
            },
            {
                "author": users[1],
                "name": "Быстрый перекус",
                "text": "Соберите блюдо и украсьте по вкусу.",
                "cooking_time": 7,
                "tags": tags[:1],
                "ingredients": ingredients[:1],
            },
            {
                "author": users[0],
                "name": "Праздничное блюдо",
                "text": "Запекайте до золотистой корочки.",
                "cooking_time": 45,
                "tags": tags[1:3] or tags[:1],
                "ingredients": ingredients[:3],
            },
            {
                "author": users[1],
                "name": "Домашний десерт",
                "text": "Охладите перед подачей.",
                "cooking_time": 20,
                "tags": tags[2:3] or tags[:1],
                "ingredients": ingredients[:2],
            },
        ]
        for index, data in enumerate(recipes):
            image_content = self.create_recipe_image(data["name"], index)
            recipe, created = Recipe.objects.get_or_create(
                name=data["name"],
                author=data["author"],
                defaults={
                    "text": data["text"],
                    "cooking_time": data["cooking_time"],
                },
            )
            recipe.image.save(image_content.name, image_content, save=False)
            recipe.text = data["text"]
            recipe.cooking_time = data["cooking_time"]
            recipe.save()
            recipe.tags.set(data["tags"])
            if not created:
                continue
            RecipeIngredient.objects.bulk_create(
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient,
                    amount=100 + index * 50,
                )
                for index, ingredient in enumerate(data["ingredients"])
            )

    def create_recipe_image(self, name, index):
        primary, secondary = IMAGE_COLORS[index % len(IMAGE_COLORS)]
        image = Image.new("RGB", IMAGE_SIZE, primary)
        draw = ImageDraw.Draw(image)
        width, height = IMAGE_SIZE

        for y in range(height):
            ratio = y / height
            color = tuple(
                int(
                    int(primary.lstrip("#")[i: i + 2], 16) * (1 - ratio)
                    + int(secondary.lstrip("#")[i: i + 2], 16) * ratio
                )
                for i in (0, 2, 4)
            )
            draw.line([(0, y), (width, y)], fill=color)

        draw.ellipse(
            (270, 95, 630, 455),
            fill="#fff7ec",
            outline="#ffffff",
            width=8,
        )
        draw.ellipse(
            (345, 170, 555, 380),
            fill=secondary,
            outline="#ffffff",
            width=5,
        )
        draw.rounded_rectangle((90, 110, 135, 420), radius=22, fill="#ffffff")
        draw.rounded_rectangle((765, 110, 810, 420), radius=22, fill="#ffffff")
        draw.ellipse((190, 80, 260, 150), fill="#ffffff")
        draw.ellipse((640, 370, 710, 440), fill="#ffffff")

        font = ImageFont.load_default()
        draw.rounded_rectangle((70, 390, 830, 488), radius=28, fill="#ffffff")
        draw.text((110, 426), name, fill="#222222", font=font)

        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)
        safe_name = name.replace(" ", "_")
        return ContentFile(buffer.read(), name=f"{safe_name}.png")
