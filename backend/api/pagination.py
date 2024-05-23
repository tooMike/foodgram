from rest_framework.pagination import PageNumberPagination


class FoodgramPagination(PageNumberPagination):
    """Пагинация c переметром limit."""

    page_size_query_param = "limit"
    page_size = 10
