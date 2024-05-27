from io import BytesIO

from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from recipes.models import Recipe, RecipeIngredient


def add_recipe_to_list(request, serializer, pk):
    """
    Базовая функция для добавления или удаления рецепта
    из избранного или списка покупок.
    """
    data = {"user": request.user.id, "recipe": pk}
    serializer = serializer(data=data, context={"request": request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def delete_recipe_from_list(request, pk, model):
    """Удаляем рецепт из списка."""
    recipe = get_object_or_404(Recipe, pk=pk)
    # Проверяем, есть ли рецепт в списке пользователя
    object_to_delete = model.objects.filter(
        user=request.user,
        recipe=recipe
    ).first()
    # Если рецепта в списке нет, возвращаем ошибку
    if not object_to_delete:
        return Response(
            {"errors": "Этого рецепта нет в указанном списке"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    # Если объект найден, удаляем его
    object_to_delete.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


def create_file_for_shopping_cart(ingredients):
    """Создание и отправка файла со списком ингредиентов."""
    # Создаем файл
    virtual_file = BytesIO()
    for item in ingredients:
        virtual_file.write(
            f'{item["ingredient__name"]} – '
            f'{item["amount"]} '
            f'{item["ingredient__measurement_unit"]}\n'.encode("utf-8")
        )
    virtual_file.seek(0)

    # Отправляем файл пользователю
    response = FileResponse(
        virtual_file,
        as_attachment=True,
        filename="Shopping List.txt",
        content_type="text/plain",
    )
    return response


def add_ingredients_to_recipeingredient(recipe, ingredients):
    """Метод для добавления ингредиентов к рецептам в промежуточную модель."""
    RecipeIngredient.objects.bulk_create(
        [
            RecipeIngredient(
                ingredient=ingredient["id"],
                amount=ingredient["amount"],
                recipe=recipe,
            )
            for ingredient in ingredients
        ]
    )
