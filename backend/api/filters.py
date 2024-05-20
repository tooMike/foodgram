from django_filters import rest_framework as filters
from django_filters.filters import (CharFilter,
                                    MultipleChoiceFilter, ModelMultipleChoiceFilter)
from rest_framework.filters import SearchFilter

from recipes.models import Recipe, Tag
from api.constants import FilterStatus



class IngredientSearchFilter(SearchFilter):
    search_param = 'name'


class RecipeFilter(filters.FilterSet):
    author = CharFilter(field_name='author')
    tags = ModelMultipleChoiceFilter(field_name='tags__slug', queryset=Tag.objects.all(), to_field_name='slug', conjoined=False)

    class Meta:
        model = Recipe
        fields = ('author', 'tags')
