from django.contrib.auth import get_user_model
from django.shortcuts import render
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from api.serializers import AvatarSerializer, IngredientSerialiser
from recipes.models import Ingredient

User = get_user_model()


class AvatarViewSet(
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet
):
    """Представление для изменения и удаления аватара."""

    serializer_class = AvatarSerializer

    def get_object(self):
        """Получаем текущего пользователя из запроса."""
        user = self.request.user
        return user

    def perform_destroy(self, instance):
        # Удаляем файл аватара, если он есть
        if instance.avatar:
            instance.avatar.delete(save=False)
        instance.save()


class IngredientViewSet(viewsets.ModelViewSet):
    """Представление для получения ингридиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerialiser
    http_method_names = ('get',)
