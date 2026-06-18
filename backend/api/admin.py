from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Subscription,
    Tag,
    User,
)


@admin.register(User)
class FoodgramUserAdmin(UserAdmin):
    list_display = ("id", "email", "username", "first_name", "last_name")
    search_fields = ("email", "username", "first_name", "last_name")
    ordering = ("id",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "measurement_unit")
    search_fields = ("name",)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "author",
        "cooking_time",
        "favorites_count",
    )
    list_filter = ("tags",)
    search_fields = ("name", "author__email", "author__username")
    inlines = (RecipeIngredientInline,)

    @admin.display(description="Добавлений в избранное")
    def favorites_count(self, obj):
        return Favorite.objects.filter(recipe=obj).count()


admin.site.register(Favorite)
admin.site.register(ShoppingCart)
admin.site.register(Subscription)
