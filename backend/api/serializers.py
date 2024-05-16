from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import Ingredient, Recipe, RecipeIngredient, RecipeTag, Tag
from users.constants import PASSWORD_MAX_LENGTH

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователей."""

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'password')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        """
        Сохраняем пользователя через create_user,
        чтобы пароль в БД записал в зашифрованном виде.
        """
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователей."""

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'avatar')


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для аватаров."""

    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)


class IngredientSerialiser(serializers.ModelSerializer):
    """Сериализатор для ингридиентов."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerialiser(serializers.ModelSerializer):
    """Сериализатор для тегов."""

    class Meta:
        model = Tag
        fields = '__all__'


class RecipeIngredientGetSerializer(serializers.ModelSerializer):
    """
    Сериализатор для получения данных
    из промежуточной модели RecipeIngredient.
    """

    id = serializers.ReadOnlyField(
        source='ingredient.id'
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name'
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta():
        model = RecipeIngredient
        fields = ('amount', 'id', 'name', 'measurement_unit')


class RecipeGetSerialiser(serializers.ModelSerializer):
    """Сериализатор для получения рецептов."""

    image = Base64ImageField()
    author = UserSerializer()
    tags = TagSerialiser(many=True)
    ingredients = RecipeIngredientGetSerializer(many=True, source='recipeingredient')

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'name', 'image', 'text', 'cooking_time')


class RecipeIngredientPostSerialiser(serializers.ModelSerializer):
    """
    Сериализатор для записи данных
    в промежуточную модель RecipeIngredient.
    """

    id = serializers.PrimaryKeyRelatedField(
        queryset = Ingredient.objects.all(),
    )

    class Meta():
        model = RecipeIngredient
        fields = ('amount', 'id')


class RecipePostSerialiser(serializers.ModelSerializer):
    """Сериализатор для добавления рецептов."""

    image = Base64ImageField()
    ingredients = RecipeIngredientPostSerialiser(
        many=True,
        source='recipeingredient'
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time')

    def create(self, validated_data):
        ingredients = validated_data.pop('recipeingredient')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)

        for tag in tags:
            RecipeTag.objects.create(tag=tag, recipe=recipe)

        for ingredient in ingredients:
            RecipeIngredient.objects.create(ingredient=ingredient['id'], amount=ingredient['amount'], recipe=recipe)
        
        return recipe
    
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('recipeingredient')
        tags = validated_data.pop('tags')
        
        # Удаляем и перезаписывам теги
        RecipeTag.objects.filter(recipe=instance).delete()
        for tag in tags:
            instance.recipetag.create(tag=tag, recipe=instance)
        
        # Удаляем и перезаписывам ингредиенты
        RecipeIngredient.objects.filter(recipe=instance).delete()
        for ingredient in ingredients:
            instance.recipeingredient.create(ingredient=ingredient['id'], amount=ingredient['amount'], recipe=instance)

        instance.save()
        return instance
    
    
