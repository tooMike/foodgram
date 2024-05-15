from rest_framework.pagination import PageNumberPagination


class UsersPagination(PageNumberPagination):
    """Пагинация для списка пользователей."""
    page_size = 10


class RecipePagination(PageNumberPagination):
    """Пагинация для списка пользователей."""
    page_size = 10