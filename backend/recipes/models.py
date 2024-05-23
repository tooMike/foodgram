from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from recipes.constants import (MEASUREMENT_NAME_MAX_LENGHT, NAME_MAX_LENGHT,
                               TAG_NAME_MAX_LENGHT, MeasurementUnit)

User = get_user_model()


class Ingredient(models.Model):
    """Модель ингредиентов."""

    name = models.CharField("Название", max_length=NAME_MAX_LENGHT)
    measurement_unit = models.CharField(
        "Единицы измерения",
        choices=MeasurementUnit.choices,
        max_length=MEASUREMENT_NAME_MAX_LENGHT
    )

    class Meta:
        verbose_name = "ингредиент"
        verbose_name_plural = "Ингредиенты"
        default_related_name = "ingredients"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Модель тегов."""

    name = models.CharField("Название", max_length=TAG_NAME_MAX_LENGHT)
    slug = models.SlugField("Slug")

    class Meta:
        verbose_name = "тег"
        verbose_name_plural = "Теги"
        default_related_name = "tags"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецептов."""

    name = models.CharField("Название", max_length=NAME_MAX_LENGHT)
    image = models.ImageField("Картинка", upload_to="recipes/images")
    text = models.TextField("Описание")
    cooking_time = models.PositiveSmallIntegerField(
        "Время приготовления", validators=(MinValueValidator(1),)
    )
    created_at = models.DateTimeField("Время добавления", auto_now_add=True)
    author = models.ForeignKey(
        User,
        verbose_name="Автор",
        on_delete=models.CASCADE,
        related_name="author_recipes",
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredient",
        verbose_name="Ингредиенты",
        related_name="ingredients_recipes",
    )
    tags = models.ManyToManyField(
        Tag, through="RecipeTag",
        verbose_name="Теги",
        related_name="tags_recipes"
    )

    class Meta:
        verbose_name = "рецепт"
        verbose_name_plural = "Рецепты"
        default_related_name = "recipes"
        ordering = ("-created_at",)

    def __str__(self):
        return self.name


class RecipeTag(models.Model):
    """Промежуточная модель тегов и рецептов."""

    recipe = models.ForeignKey(
        Recipe,
        verbose_name="Рецепт",
        on_delete=models.CASCADE
    )
    tag = models.ForeignKey(Tag, verbose_name="Тег", on_delete=models.CASCADE)

    class Meta:
        default_related_name = "recipetag"


class RecipeIngredient(models.Model):
    """Промежуточная модель ингредиентов и рецептов."""

    recipe = models.ForeignKey(
        Recipe,
        verbose_name="Рецепт",
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient, verbose_name="Ингредиент", on_delete=models.CASCADE
    )
    amount = models.PositiveSmallIntegerField(
        "Количество", validators=(MinValueValidator(1),)
    )

    class Meta:
        default_related_name = "recipeingredient"
