from django.conf import settings
from rest_framework.pagination import PageNumberPagination


class FoodgramPagination(PageNumberPagination):
    """Пагинация c переметром limit."""

    page_size_query_param = "limit"
    page_size = settings.DEFAULT_PAGE_SIZE
