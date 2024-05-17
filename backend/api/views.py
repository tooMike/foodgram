from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.conf import settings
from djoser.serializers import SetPasswordSerializer
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.filters import IngredientSearchFilter, RecipeFilter
from api.pagination import RecipePagination, UsersPagination
from api.permissions import IsAuthor, IsCurrentUser
from api.serializers import (AvatarSerializer, IngredientSerialiser,
                             RecipeGetSerialiser, RecipePostSerialiser,
                             SubscriptionsSerializer, TagSerialiser,
                             UserRegistrationSerializer, UserSerializer, RecipeFavoriteGetSerialiser)
from recipes.models import Ingredient, Recipe, Tag

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    Создаем своей ViewSet, взяв за основу UserViewSet из djoser,
    чтобы оставить только нужный функционал
    """

    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    lookup_field = settings.USER_ID_FIELD
    pagination_class = UsersPagination

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
        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)

    @action(["patch", "delete", "put"], detail=False, url_path='me/avatar')
    def avatar(self, request):
        user = self.get_instance()
        # Если метод PATCH, то добавляем аватар
        # if request.method == "PATCH":
        if request.method == "PUT":
            serializer = self.get_serializer(
                user,
                data=request.data,
                context={'request': request}
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
                {"errors": 'Подписка/отписка на самого себя невозможна'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.method == "POST":
            if user.subscriptions.filter(id=followee.id).exists():
                return Response(
                    {"errors": "Вы уже подписаны на этого пользователя"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.subscriptions.add(followee)
            serializer = SubscriptionsSerializer(
                followee,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == "DELETE":
            if user.subscriptions.filter(id=followee.id).exists():
                user.subscriptions.remove(followee)
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {"errors": "Вы не были подписаны на этого пользователя"},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(["get"], permission_classes=(IsAuthenticated,), detail=False)
    def subscriptions(self, request):
        """Получаем список подписок текущего пользователя."""
        user = self.get_instance()
        subscriptions = user.subscriptions.all()

        # Добавляем пагинацию
        paginator = UsersPagination()
        page = paginator.paginate_queryset(subscriptions, request)
        if page is not None:
            serializer = SubscriptionsSerializer(
                page,
                many=True,
                context={'request': request}
            )
            return paginator.get_paginated_response(serializer.data)
        
        serializer = SubscriptionsSerializer(
            subscriptions,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)


class IngredientViewSet(viewsets.ModelViewSet):
    """Представление для получения ингридиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerialiser
    http_method_names = ('get',)
    permission_classes = (AllowAny,)
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('name',)


class TagViewSet(viewsets.ModelViewSet):
    """Представление для получения тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerialiser
    http_method_names = ('get',)
    permission_classes = (AllowAny,)


class RecipeViewSet(viewsets.ModelViewSet):
    """Представление для рецептов."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeGetSerialiser
    http_method_names = ('get', 'post', 'patch', 'delete')
    pagination_class = RecipePagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'partial_update':
            return RecipePostSerialiser
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action == 'create':
            return (IsAuthenticated(),)
        elif self.action == 'partial_update' or self.action == 'delete':
            return (IsAuthor(),)
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        recipe = serializer.save(author=self.request.user)
        headers = self.get_success_headers(serializer.data)
        response_serializer = RecipeGetSerialiser(recipe, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        recipe = serializer.save()
        headers = self.get_success_headers(serializer.data)
        response_serializer = RecipeGetSerialiser(recipe, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_200_OK, headers=headers)
    
    @action(["get"], detail=True, url_path='get-link')
    def get_link(self, request, pk=None):
        """Получаем короткую ссылку на рецепт."""
        return Response({"short-link": "https://foodgram.example.org/s/3d0"}, status=status.HTTP_200_OK)

    @action(["post"], detail=True, permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk=None):
        """Добавляем рецепт в избранное."""
        # Проверяем, существует ли такой рецепт
        if not Recipe.objects.filter(pk=pk).first():
            return Response(
                {"errors": "Такого рецепта не существует"},
                status=status.HTTP_400_BAD_REQUEST
            )
        recipe = Recipe.objects.get(pk=pk)
        user = request.user
        # Проверяем, если ли такой рецепт уже в избранном
        if user.favorites.filter(id=pk):
            return Response(
                {"errors": "Этот рецепт уже есть в избранном"},
                status=status.HTTP_400_BAD_REQUEST
            )
        recipe.user_favorites_recipes.add(user)
        serializer = RecipeFavoriteGetSerialiser(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
