from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.filters import IngredientSearchFilter, RecipeFilter
from api.mixins import GetListViewSet
from api.pagination import FoodgramPagination
from api.permissions import IsAuthorOrReadOnly
from api.recipes_utils import (add_recipe_to_list,
                               create_file_for_shopping_cart,
                               delete_recipe_from_list)
from api.serializers import (AvatarSerializer, IngredientSerialiser,
                             RecipeGetSerialiser, RecipePostSerialiser,
                             RecipeToFavoriteSerializer,
                             RecipeToShoppingListSerializer,
                             SubscriptionsSerializer, TagSerialiser,
                             UserSubscriptionSerializer)
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.models import UserFavorite, UserShoppingList, UserSubscriptions

User = get_user_model()


class UserViewSet(UserViewSet):
    """Модифицируем UserViewSet из djoser."""

    pagination_class = FoodgramPagination

    def get_permissions(self):
        if self.action == "me":
            return (IsAuthenticated(),)
        return super().get_permissions()

    @action(
        ["delete", "put"],
        detail=False,
        url_path="me/avatar",
        permission_classes=[IsAuthenticated],
        serializer_class=AvatarSerializer,
    )
    def avatar(self, request):
        """Представление для взаимодействия пользователя со своим аватаром"""
        user = request.user
        # Метод PUT вместо PATCH, так как фронт работает именно с PUT
        if request.method == "PUT":
            serializer = self.get_serializer(
                user, data=request.data, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        # Иначе удаляем аватар
        if user.avatar:
            user.avatar.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        ["post", "delete"],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id=None):
        """
        Подписываем или удаляем подписку текущего пользователя
        на другого пользователя.
        """
        user = self.request.user
        subscription = get_object_or_404(User, pk=id)
        data = {"user": user.id, "subscription": subscription.id}
        if request.method == "POST":
            serializer = UserSubscriptionSerializer(
                data=data, context={"request": request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        subscription = UserSubscriptions.objects.filter(
            user=user, subscription=subscription
        ).first()
        if subscription:
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"errors": "Вы не были подписаны на этого пользователя"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(["get"], permission_classes=(IsAuthenticated,), detail=False)
    def subscriptions(self, request):
        """Получаем список подписок текущего пользователя."""
        user = self.request.user
        subscriptions = user.subscriptions.all()
        # Добавляем пагинацию
        page = self.paginate_queryset(subscriptions)
        serializer = SubscriptionsSerializer(
            page, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)


class IngredientViewSet(GetListViewSet):
    """Представление для получения ингридиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerialiser
    permission_classes = (AllowAny,)
    filter_backends = (IngredientSearchFilter,)
    search_fields = ("name",)


class TagViewSet(GetListViewSet):
    """Представление для получения тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerialiser
    permission_classes = (AllowAny,)


class RecipeViewSet(viewsets.ModelViewSet):
    """Представление для рецептов."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeGetSerialiser
    http_method_names = ("get", "post", "patch", "delete")
    pagination_class = FoodgramPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsAuthorOrReadOnly,)

    def get_serializer_class(self):
        if self.action in ("create", "partial_update"):
            return RecipePostSerialiser
        return super().get_serializer_class()

    @action(["get"], detail=True, url_path="get-link")
    def get_link(self, request, pk=None):
        """Формируем короткую ссылку на рецепт."""
        short_url_code = Recipe.objects.get(pk=pk).short_url_code
        short_url = request.build_absolute_uri(f"/s/{short_url_code}")
        return Response(
            {"short-link": short_url},
            status=status.HTTP_200_OK,
        )

    @action(
        ["post", "delete"],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        if request.method == "POST":
            return add_recipe_to_list(
                request=request, pk=pk, serializer=RecipeToFavoriteSerializer
            )
        return delete_recipe_from_list(
            request=request,
            pk=pk,
            model=UserFavorite
        )

    @action(["post", "delete"], detail=True, permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk=None):
        if request.method == "POST":
            return add_recipe_to_list(
                request=request, pk=pk, serializer=RecipeToShoppingListSerializer
            )
        return delete_recipe_from_list(request=request, pk=pk, model=UserShoppingList)

    @action(["get"], detail=False, permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        """Скачивание ингридиентов из списка покупок."""
        user = request.user

        ingredients = (
            RecipeIngredient.objects.filter(
                recipe__usershoppinglist__user=user
            ).values(
                "ingredient__name", "ingredient__measurement_unit"
            ).annotate(
                amount=Sum("amount")
            ).order_by("ingredient__name")
        )

        return create_file_for_shopping_cart(ingredients)
