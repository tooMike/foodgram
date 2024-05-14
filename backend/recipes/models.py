from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from recipes.constants import (NAME_MAX_LENGHT, TAG_NAME_MAX_LENGHT,
                               MeasurementUnit)

User = get_user_model()


class Ingredient(models.Model):
    """Модель ингридиентов."""

    name = models.CharField("Название", max_length=NAME_MAX_LENGHT)
    measurement_unit = models.CharField(
        "Единицы измерения", choices=MeasurementUnit.choices, max_length=10
    )


class Tag(models.Model):
    """Модель тегов."""

    name = models.CharField("Название", max_length=TAG_NAME_MAX_LENGHT)
    slug = models.SlugField("Slug")


class Recipe(models.Model):
    """Модель рецептов."""

    name = models.CharField("Название", max_length=NAME_MAX_LENGHT)
    image = models.ImageField("Картинка", upload_to="media")
    text = models.TextField("Описание")
    cooking_time = models.PositiveSmallIntegerField(
        "Время приготовления", validators=(MinValueValidator(1),)
    )
    author = models.ForeignKey(
        User,
        verbose_name="Автор",
        on_delete=models.CASCADE,
        related_name="author_recipes",
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name="Ингридиенты",
        related_name="ingredients_recipes"
    )
    tags = models.ManyToManyField(Tag, verbose_name="Теги")
    favorites = models.ManyToManyField(
        User,
        verbose_name="Избранные рецепты",
        related_name="favorites_recipes"
    )
    shopping_list = models.ManyToManyField(
        User,
        verbose_name="Список покупок",
        related_name="shopping_list_recipes"
    )
