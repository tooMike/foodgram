from rest_framework import permissions


class IsCurrentUser(permissions.IsAuthenticated):
    """Разрешаем доступ только владельцу."""

    def has_object_permission(self, request, view, obj):
        user = request.user
        return obj.pk == user.pk


class IsAuthor(permissions.IsAuthenticated):
    """Разрешаем доступ только автору."""

    def has_object_permission(self, request, view, obj):
        user = request.user
        return obj.author == user
