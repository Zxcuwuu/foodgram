from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .filters import RecipeFilter
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from users.models import User
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    AvatarSerializer,
    IngredientSerializer,
    RecipeMinifiedSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    SetPasswordSerializer,
    TagSerializer,
    TokenCreateSerializer,
    UserCreateSerializer,
    UserSerializer,
    UserWithRecipesSerializer,
)


class UserViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = User.objects.all()
    http_method_names = ("get", "post", "put", "delete")

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        if self.action in ("subscriptions", "subscribe"):
            return UserWithRecipesSerializer
        if self.action == "avatar":
            return AvatarSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action in (
            "me",
            "set_password",
            "avatar",
            "subscriptions",
            "subscribe",
        ):
            return (IsAuthenticated(),)
        return (AllowAny(),)

    @action(detail=False, methods=("get",), url_path="me")
    def me(self, request):
        return Response(
            UserSerializer(request.user, context={"request": request}).data
        )

    @action(detail=False, methods=("post",), url_path="set_password")
    def set_password(self, request):
        serializer = SetPasswordSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=("put", "delete"), url_path="me/avatar")
    def avatar(self, request):
        if request.method == "DELETE":
            request.user.avatar.delete(save=False)
            request.user.avatar = None
            request.user.save(update_fields=("avatar",))
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = AvatarSerializer(
            request.user,
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=("get",), url_path="subscriptions")
    def subscriptions(self, request):
        queryset = User.objects.filter(subscribers__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = UserWithRecipesSerializer(
            page,
            many=True,
            context={"request": request},
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=("post", "delete"), url_path="subscribe")
    def subscribe(self, request, pk=None):
        author = self.get_object()
        if request.method == "DELETE":
            deleted, _ = request.user.subscriptions.filter(
                author=author,
            ).delete()
            if not deleted:
                return Response(
                    {"errors": "Подписка не найдена."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(status=status.HTTP_204_NO_CONTENT)
        if author == request.user:
            return Response(
                {"errors": "Нельзя подписаться на себя."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        subscription, created = request.user.subscriptions.get_or_create(
            author=author,
        )
        if not created:
            return Response(
                {"errors": "Вы уже подписаны на этого пользователя."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = UserWithRecipesSerializer(
            subscription.author,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = Ingredient.objects.all()
        name = self.request.query_params.get("name")
        if name:
            queryset = queryset.filter(name__istartswith=name)
        return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.select_related("author").prefetch_related(
        "tags",
        "recipe_ingredients__ingredient",
    )
    permission_classes = (IsAuthorOrReadOnly,)
    filterset_class = RecipeFilter
    http_method_names = ("get", "post", "patch", "delete")

    def get_permissions(self):
        if self.action in (
            "create",
            "favorite",
            "shopping_cart",
            "download_shopping_cart",
        ):
            return (IsAuthenticated(),)
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def get_queryset(self):
        return super().get_queryset().distinct()

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = False
        return self.update(request, *args, **kwargs)

    def _recipe_relation(self, request, pk, relation_model):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == "DELETE":
            deleted, _ = relation_model.objects.filter(
                user=request.user,
                recipe=recipe,
            ).delete()
            if not deleted:
                return Response(
                    {"errors": "Рецепт не был добавлен."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(status=status.HTTP_204_NO_CONTENT)
        relation, created = relation_model.objects.get_or_create(
            user=request.user,
            recipe=recipe,
        )
        if not created:
            return Response(
                {"errors": "Рецепт уже добавлен."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = RecipeMinifiedSerializer(
            relation.recipe,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=("post", "delete"))
    def favorite(self, request, pk=None):
        return self._recipe_relation(request, pk, Favorite)

    @action(detail=True, methods=("post", "delete"))
    def shopping_cart(self, request, pk=None):
        return self._recipe_relation(request, pk, ShoppingCart)

    @action(detail=False, methods=("get",), url_path="download_shopping_cart")
    def download_shopping_cart(self, request):
        ingredients = (
            RecipeIngredient.objects.filter(
                recipe__shoppingcart__user=request.user,
            )
            .values("ingredient__name", "ingredient__measurement_unit")
            .annotate(total=Sum("amount"))
            .order_by("ingredient__name")
        )
        lines = ["Список покупок:"]
        for item in ingredients:
            lines.append(
                f"{item['ingredient__name']} "
                f"({item['ingredient__measurement_unit']}) - {item['total']}"
            )
        content = "\n".join(lines)
        response = HttpResponse(
            content,
            content_type="text/plain; charset=utf-8",
        )
        response["Content-Disposition"] = (
            'attachment; filename="shopping-list.txt"'
        )
        return response

    @action(detail=True, methods=("get",), url_path="get-link")
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        return Response(
            {"short-link": request.build_absolute_uri(f"/recipes/{recipe.id}")}
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def token_login(request):
    serializer = TokenCreateSerializer(
        data=request.data,
        context={"request": request},
    )
    serializer.is_valid(raise_exception=True)
    return Response(serializer.save())


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def token_logout(request):
    Token.objects.filter(user=request.user).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
@permission_classes([AllowAny])
def reset_password(request):
    return Response(status=status.HTTP_204_NO_CONTENT)
