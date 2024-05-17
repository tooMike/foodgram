from django_filters import rest_framework as filters
from django_filters.filters import (CharFilter,
                                    MultipleChoiceFilter)
from rest_framework.filters import SearchFilter

from recipes.models import Recipe, Tag



class IngredientSearchFilter(SearchFilter):
    search_param = 'name'


class RecipeFilter(filters.FilterSet):
    author = CharFilter(field_name='author')
    
    # Получение списка возможных тегов
    tags_choices = Tag.objects.values_list('slug', flat=True).distinct()
    tags = MultipleChoiceFilter(field_name='tags__slug', choices=[(tag, tag) for tag in tags_choices], conjoined=False)

    class Meta:
        model = Recipe
        fields = ('author', 'tags')
