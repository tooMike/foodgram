from django.contrib import admin

from recipes.models import Ingredient, Recipe, RecipeIngredient, RecipeTag, Tag


class RecipeIngredientInline(admin.TabularInline):
    """Добавляем ингредиенты рецепта."""

    model = RecipeIngredient
    extra = 1


class RecipeTagInline(admin.TabularInline):
    """Добавляем теги рецепта."""

    model = RecipeTag
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    """Добавляем рецепты."""

    inlines = (RecipeIngredientInline, RecipeTagInline)


admin.site.register(Ingredient)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag)
