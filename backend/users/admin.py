from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Subscription, User


@admin.register(User)
class FoodgramUserAdmin(UserAdmin):
    list_display = ("id", "email", "username", "first_name", "last_name")
    search_fields = ("email", "username", "first_name", "last_name")
    ordering = ("id",)


admin.site.register(Subscription)
