from rest_framework import status
from rest_framework.response import Response

from api.serializers import RecipeFavoriteGetSerialiser
from recipes.models import Recipe


def add_recipe_to_list(request, pk=None, list_type='favorite'):
    """
    Базовая функция для добавления или удаления рецепта
    из избранного или списка покупок.
    """
    # Проверяем, существует ли такой рецепт
    # В ReDoc нет варианта 404 ошибки, поэтому возвращаем 400
    if not Recipe.objects.filter(pk=pk).exists():
        return Response(
            {"errors": "Такого рецепта не существует"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    list_type = (request.user.favorites if list_type == 'favorite'
                 else request.user.shopping_list)
    recipe = Recipe.objects.get(pk=pk)
    # user = request.user
    if request.method == "POST":
        # Проверяем, есть ли такой рецепт уже в избранном
        if list_type.filter(id=pk):
            return Response(
                {"errors": "Этот рецепт уже есть в избранном"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        list_type.add(recipe)
        serializer = RecipeFavoriteGetSerialiser(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    # Далее настраиваем удаление из избранного
    if not list_type.filter(id=pk):
        # Проверяем, есть ли такой рецепт в избранном
        return Response(
            {"errors": "Этого рецепта нет в избранном"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    list_type.remove(recipe)
    return Response(status=status.HTTP_204_NO_CONTENT)
