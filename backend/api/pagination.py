from rest_framework.pagination import PageNumberPagination
from rest_framework.pagination import LimitOffsetPagination


class UsersPagination(LimitOffsetPagination):
    """Пагинация для списка пользователей."""
    default_limit = 10


class RecipePagination(PageNumberPagination):
    """Пагинация для списка пользователей."""
    page_size = 10