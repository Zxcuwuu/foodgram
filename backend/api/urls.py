from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet,
    UserViewSet,
    reset_password,
    token_login,
    token_logout,
)


router = DefaultRouter()
router.register("users", UserViewSet, basename="users")
router.register("tags", TagViewSet, basename="tags")
router.register("ingredients", IngredientViewSet, basename="ingredients")
router.register("recipes", RecipeViewSet, basename="recipes")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/token/login/", token_login, name="token_login"),
    path("auth/token/logout/", token_logout, name="token_logout"),
    path("users/reset_password/", reset_password, name="reset_password"),
]
