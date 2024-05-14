from django.contrib.auth import get_user_model
from django.shortcuts import render
from djoser.conf import settings
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response

from api.serializers import AvatarSerializer, IngredientSerialiser
from recipes.models import Ingredient

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

    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = settings.PERMISSIONS.user_create
        elif self.action == "set_password":
            self.permission_classes = settings.PERMISSIONS.set_password
        elif self.action == "list":
            self.permission_classes = settings.PERMISSIONS.user_list
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "create":
            return settings.SERIALIZERS.user_create
        elif self.action == "set_password":
            return settings.SERIALIZERS.set_password
        elif self.action == "me":
            return settings.SERIALIZERS.current_user

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
            serializer = AvatarSerializer(
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
