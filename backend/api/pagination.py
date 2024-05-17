from rest_framework.pagination import LimitOffsetPagination


class UsersPagination(LimitOffsetPagination):
    """Пагинация для списка пользователей."""
    default_limit = 10


class RecipePagination(LimitOffsetPagination):
    """Пагинация для списка рецептов."""
    default_limit = 10
