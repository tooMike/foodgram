from collections import defaultdict
from io import BytesIO

from django.conf import settings as django_settings
from django.contrib.auth import get_user_model
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.conf import settings as djoser_settings
from djoser.serializers import SetPasswordSerializer
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.constants import FilterStatus
from api.filters import IngredientSearchFilter, RecipeFilter
from api.pagination import FoodgramPagination
from api.permissions import IsAuthor, IsCurrentUser
from api.recipes_utils import add_recipe_to_list
from api.serializers import (AvatarSerializer, IngredientSerialiser,
                             RecipeGetSerialiser, RecipePostSerialiser,
                             SubscriptionsSerializer, TagSerialiser,
                             UserRegistrationSerializer, UserSerializer)
from recipes.models import Ingredient, Recipe, Tag
from url_shortener.models import ShortURL
from url_shortener.shortner import generate_short_code

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    Создаем своей ViewSet, взяв за основу UserViewSet из djoser,
    чтобы оставить только нужный функционал
    """

    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    lookup_field = djoser_settings.USER_ID_FIELD
    pagination_class = FoodgramPagination

    def get_permissions(self):
        if self.action == "set_password":
            return (IsAuthenticated(),)
        elif self.action == "me" or self.action == "avatar":
            return (IsCurrentUser(),)
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "create":
            return UserRegistrationSerializer
        elif self.action == "set_password":
            return SetPasswordSerializer
        elif self.action == "avatar":
            return AvatarSerializer
        return self.serializer_class

    def get_instance(self):
        return self.request.user

    @action(["get"], detail=False)
    def me(self, request, *args, **kwargs):
        """Получение информации пользователем о себе."""
        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)

    @action(["delete", "put"], detail=False, url_path="me/avatar")
    def avatar(self, request):
        """Представление для взаимодействия пользователя со своим аватаром"""
        user = self.get_instance()
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

    @action(["post"], detail=False)
    def set_password(self, request):
        """Представление для установки пароля."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.request.user.set_password(serializer.data["new_password"])
        self.request.user.save()

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
        user = self.get_instance()
        followee = get_object_or_404(User, pk=id)
        if followee == user:
            return Response(
                {"errors": "Подписка/отписка на самого себя невозможна"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if request.method == "POST":
            if user.subscriptions.filter(id=followee.id).exists():
                return Response(
                    {"errors": "Вы уже подписаны на этого пользователя"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user.subscriptions.add(followee)
            serializer = SubscriptionsSerializer(
                followee,
                context={"request": request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == "DELETE":
            if user.subscriptions.filter(id=followee.id).exists():
                user.subscriptions.remove(followee)
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {"errors": "Вы не были подписаны на этого пользователя"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(["get"], permission_classes=(IsAuthenticated,), detail=False)
    def subscriptions(self, request):
        """Получаем список подписок текущего пользователя."""
        user = self.get_instance()
        subscriptions = user.subscriptions.all()

        # Добавляем пагинацию
        paginator = FoodgramPagination()
        page = paginator.paginate_queryset(subscriptions, request)
        if page is not None:
            serializer = SubscriptionsSerializer(
                page, many=True, context={"request": request}
            )
            return paginator.get_paginated_response(serializer.data)

        serializer = SubscriptionsSerializer(
            subscriptions, many=True, context={"request": request}
        )
        return Response(serializer.data)


class IngredientViewSet(viewsets.ModelViewSet):
    """Представление для получения ингридиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerialiser
    http_method_names = ("get",)
    permission_classes = (AllowAny,)
    filter_backends = (IngredientSearchFilter,)
    search_fields = ("name",)


class TagViewSet(viewsets.ModelViewSet):
    """Представление для получения тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerialiser
    http_method_names = ("get",)
    permission_classes = (AllowAny,)


class RecipeViewSet(viewsets.ModelViewSet):
    """Представление для рецептов."""

    serializer_class = RecipeGetSerialiser
    http_method_names = ("get", "post", "patch", "delete")
    pagination_class = FoodgramPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (AllowAny,)

    def get_queryset(self):
        """
        Добавляем в queryset опцию фильтрации по избранному
        и по списку покупок.
        """
        queryset = Recipe.objects.all()
        is_favorited = self.request.query_params.get("is_favorited")
        is_in_shopping_cart = self.request.query_params.get(
            "is_in_shopping_cart"
        )
        user = self.request.user
        if not user.is_authenticated:
            return queryset
        if is_favorited == FilterStatus.IS_ACTIVE.value:
            queryset = queryset.filter(user_favorites_recipes=user)
        if is_in_shopping_cart == FilterStatus.IS_ACTIVE.value:
            queryset = queryset.filter(user_shopping_list_recipes=user)
        return queryset

    def get_serializer_class(self):
        if self.action == "create" or self.action == "partial_update":
            return RecipePostSerialiser
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action == "create":
            return (IsAuthenticated(),)
        elif self.action == "partial_update" or self.action == "destroy":
            return (IsAuthor(),)
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        recipe = serializer.save(author=self.request.user)
        response_serializer = RecipeGetSerialiser(
            recipe,
            context={"request": request}
        )
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        recipe = serializer.save()
        response_serializer = RecipeGetSerialiser(
            recipe,
            context={"request": request}
        )
        return Response(
            response_serializer.data, status=status.HTTP_200_OK
        )

    @action(["get"], detail=True, url_path="get-link")
    def get_link(self, request, pk=None):
        """Формируем короткую ссылку на рецепт."""
        # Получаем полную ссылку на рецепт
        full_url = f"{django_settings.DOMAIN_FRONT}/recipes/{pk}/"
        # Проверяем, есть ли уже uniq_id для этой ссылки.
        # Отдаем коротнкую ссылку с ним, если uniq_id уже есть
        # или создаем новый в БД
        if ShortURL.objects.filter(full_url=full_url).exists():
            uniq_id = ShortURL.objects.get(full_url=full_url).uniq_id
        else:
            uniq_id = generate_short_code()
            # Генерируем uniq_id до тех пор,
            # пока не получим уникальное значение
            while ShortURL.objects.filter(uniq_id=uniq_id).exists():
                uniq_id = generate_short_code()
            ShortURL.objects.create(full_url=full_url, uniq_id=uniq_id)
        short_url = f"{django_settings.DOMAIN_BACK}/s/{uniq_id}"
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
        return add_recipe_to_list(request, pk, list_type='favorite')

    @action(
        ["post", "delete"],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk=None):
        return add_recipe_to_list(request, pk, list_type='shopping_cart')

    @action(["get"], detail=False, permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        """Скачивание ингридиентов из списка покупок."""
        user = request.user
        recipes = Recipe.objects.filter(
            user_shopping_list_recipes=user
        ).prefetch_related("ingredients")
        ingredients_count = defaultdict(int)

        for recipe in recipes:
            for item in recipe.recipeingredient.all().select_related(
                "ingredient"
            ):
                ingredient = item.ingredient
                ingredients_count[
                    (ingredient.name, ingredient.measurement_unit)
                ] += item.amount

        # Создаем файл
        virtual_file = BytesIO()
        for (name, unit), amount in ingredients_count.items():
            virtual_file.write(f"{name} – {amount} {unit}\n".encode("utf-8"))
        virtual_file.seek(0)

        # Отправляем файл пользователю
        response = FileResponse(
            virtual_file,
            as_attachment=True,
            filename="Shopping List.txt",
            content_type="text/plain",
        )
        return response
