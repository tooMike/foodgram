from django.contrib import admin

from recipes.models import Ingredient, Recipe, RecipeIngredient, RecipeTag, Tag


class TagAdmin(admin.ModelAdmin):
    """Отображение тегов."""

    search_fields = ("name",)


class IngredientAdmin(admin.ModelAdmin):
    """Отображение ингредиентов."""

    search_fields = ("name",)
    list_display = ("name", "measurement_unit")


class RecipeIngredientInline(admin.TabularInline):
    """Отображение ингредиентов рецепта."""

    model = RecipeIngredient
    extra = 1


class RecipeTagInline(admin.TabularInline):
    """Отображение тегов рецепта."""

    model = RecipeTag
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    """Отображение рецептов."""

    list_display = ("name", "author", "created_at", "count_favorites")
    readonly_fields = ("created_at",)

    inlines = (RecipeIngredientInline, RecipeTagInline)
    search_fields = (
        "name",
        "author__username",
        "author__first_name",
        "author__last_name",
        "tags__name",
    )
    list_filter = ('tags__name',)

    def count_favorites(self, obj):
        return obj.user_favorites_recipes.count()

    count_favorites.short_description = "Добавлений в избранное"

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        return list(readonly_fields) + ["count_favorites"]


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
