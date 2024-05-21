from django_filters import rest_framework as filters
from django_filters.filters import CharFilter, ModelMultipleChoiceFilter
from rest_framework.filters import SearchFilter

from recipes.models import Recipe, Tag


class IngredientSearchFilter(SearchFilter):
    """Фильтр для ингредиентов рецепта."""
    search_param = "name"


class RecipeFilter(filters.FilterSet):
    """Фильтр для рецептов."""
    author = CharFilter(field_name="author")
    tags = ModelMultipleChoiceFilter(
        field_name="tags__slug",
        queryset=Tag.objects.all(),
        to_field_name="slug",
        conjoined=False,
    )

    class Meta:
        model = Recipe
        fields = ("author", "tags")
