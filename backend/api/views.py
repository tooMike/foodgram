from django.contrib.auth import get_user_model
from djoser.conf import settings
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.pagination import RecipePagination, UsersPagination
from api.serializers import (IngredientSerialiser, RecipeGetSerialiser,
                             RecipePostSerialiser, TagSerialiser)
from recipes.models import Ingredient, Recipe, Tag
from api.permissions import IsAuthor

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    Создаем своей ViewSet, взяв за основу UserViewSet из djoser,
    чтобы оставить только нужный функционал
    """

    serializer_class = settings.SERIALIZERS.user
    queryset = User.objects.all()
    permission_classes = settings.PERMISSIONS.user
    lookup_field = settings.USER_ID_FIELD
    pagination_class = UsersPagination

    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = settings.PERMISSIONS.user_create
        elif self.action == "set_password":
            self.permission_classes = settings.PERMISSIONS.set_password
        elif self.action == "list":
            self.permission_classes = settings.PERMISSIONS.user_list
        elif self.action == "me":
            self.permission_classes = settings.PERMISSIONS.me
        elif self.action == "avatar":
            self.permission_classes = settings.PERMISSIONS.me
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "create":
            return settings.SERIALIZERS.user_create
        elif self.action == "set_password":
            return settings.SERIALIZERS.set_password
        elif self.action == "me":
            return settings.SERIALIZERS.current_user
        elif self.action == "avatar":
            return settings.SERIALIZERS.avatar

        return self.serializer_class

    def get_instance(self):
        return self.request.user

    @action(["get"], detail=False)
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)

    @action(["patch", "delete"], detail=False, url_path='me/avatar')
    def avatar(self, request):
        user = self.get_instance()
        # Если метод PATCH, то добавляем аватар
        if request.method == "PATCH":
            serializer = self.get_serializer(
                user, data=request.data, partial=True
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


class IngredientViewSet(viewsets.ModelViewSet):
    """Представление для получения ингридиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerialiser
    http_method_names = ('get',)
    permission_classes = (AllowAny,)


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

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'partial_update':
            return RecipePostSerialiser
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = (IsAuthenticated,)
        elif self.action == 'partial_update' or self.action == 'delete':
            permission_classes = (IsAuthor,)
        else:
            permission_classes = (AllowAny,)
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        recipe = serializer.save(author=self.request.user)
        headers = self.get_success_headers(serializer.data)
        response_serializer = RecipeGetSerialiser(recipe)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        recipe = serializer.save()
        headers = self.get_success_headers(serializer.data)
        response_serializer = RecipeGetSerialiser(recipe)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)
