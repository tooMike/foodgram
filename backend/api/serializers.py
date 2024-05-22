from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import Ingredient, Recipe, RecipeIngredient, RecipeTag, Tag


User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователей."""

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "password"
        )
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        """
        Сохраняем пользователя через create_user,
        чтобы пароль в БД записал в зашифрованном виде.
        """
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователей."""

    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        """
        Проверяем, подписан ли текущий пользователь
        на сериализуемого пользователя
        """
        # Получаем текущего пользователя
        user = self.context.get("request").user
        # Для анонимных пользователей всегда возвращаем False
        if user.is_anonymous:
            return False
        # Проверяем, что в подписках текущего пользователя
        # есть запрашиваемый пользователь
        return user.subscriptions.filter(id=obj.id).exists()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "avatar",
            "is_subscribed",
        )


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для аватаров."""

    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ("avatar",)

    def validate_avatar(self, value):
        """Проверяем, что передано не пустое поле."""
        if value is None:
            raise ValidationError("Передано пустое поле avatar")
        return value

    def update(self, instance, validated_data):
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.save()
        return instance


class IngredientSerialiser(serializers.ModelSerializer):
    """Сериализатор для ингридиентов."""

    class Meta:
        model = Ingredient
        fields = "__all__"


class TagSerialiser(serializers.ModelSerializer):
    """Сериализатор для тегов."""

    class Meta:
        model = Tag
        fields = "__all__"


class RecipeIngredientGetSerializer(serializers.ModelSerializer):
    """
    Сериализатор для получения данных
    из промежуточной модели RecipeIngredient.
    """

    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = RecipeIngredient
        fields = ("amount", "id", "name", "measurement_unit")


class RecipeGetSerialiser(serializers.ModelSerializer):
    """Сериализатор для получения рецептов."""

    image = Base64ImageField()
    author = UserSerializer()
    tags = TagSerialiser(many=True)
    ingredients = RecipeIngredientGetSerializer(
        many=True,
        source="recipeingredient"
    )

    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_is_favorited(self, obj):
        """Проверяем, есть ли рецепт в избранном пользователя."""
        user = self.context.get("request").user
        # Проверяем, аутентифицирован ли пользователь
        if not user.is_authenticated:
            return False
        if user.favorites.filter(id=obj.id):
            return True
        return False

    def get_is_in_shopping_cart(self, obj):
        """Проверяем, есть ли рецепт в списке покупок пользователя."""
        user = self.context.get("request").user
        # Проверяем, аутентифицирован ли пользователь
        if not user.is_authenticated:
            return False
        if user.shopping_list.filter(id=obj.id):
            return True
        return False

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
            "is_favorited",
            "is_in_shopping_cart",
        )


class RecipeFavoriteGetSerialiser(serializers.ModelSerializer):
    """Сериализатор для получения рецептов при добавлении в избранное."""

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class RecipeIngredientPostSerialiser(serializers.ModelSerializer):
    """
    Сериализатор для записи данных
    в промежуточную модель RecipeIngredient.
    """

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
    )

    class Meta:
        model = RecipeIngredient
        fields = ("amount", "id")


class RecipePostSerialiser(serializers.ModelSerializer):
    """Сериализатор для добавления рецептов."""

    image = Base64ImageField()
    ingredients = RecipeIngredientPostSerialiser(
        many=True,
        source="recipeingredient"
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )

    class Meta:
        model = Recipe
        fields = (
            "ingredients",
            "tags",
            "image",
            "name",
            "text",
            "cooking_time"
        )

    def validate_image(self, value):
        if value in [None, ""]:
            raise serializers.ValidationError(
                "Картинка обязательно должна быть добавлена"
            )
        return value

    def validate_tags(self, value):
        """Проверка, что список тегов не пуст."""
        if not value:
            raise serializers.ValidationError(
                "Необходимо указать хотя бы один тег."
            )
        if len(value) != len(set(value)):
            raise serializers.ValidationError(
                "Теги не должны повторяться."
            )
        return value

    def validate_ingredients(self, value):
        """Проверка, что список ингредиентов не пуст."""
        if not value:
            raise serializers.ValidationError(
                "Необходимо указать хотя бы один ингредиент."
            )
        for item in value:
            for second_item in value[value.index(item) + 1:]:
                if item["id"] == second_item["id"]:
                    raise serializers.ValidationError(
                        "Ингредиенты не должны повторяться."
                    )
        return value

    def create(self, validated_data):
        ingredients = validated_data.pop("recipeingredient")
        tags = validated_data.pop("tags")
        image = validated_data.pop("image")
        recipe = Recipe.objects.create(**validated_data, image=image)

        # Добавляем теги в промежуточную модель
        RecipeTag.objects.bulk_create(
            [RecipeTag(tag=tag, recipe=recipe) for tag in tags]
        )

        # Добавляем ингридиенты в промежуточную модель
        RecipeIngredient.objects.bulk_create(
            [RecipeIngredient(
                ingredient=ingredient["id"],
                amount=ingredient["amount"],
                recipe=recipe,
            ) for ingredient in ingredients]
        )

        return recipe

    def update(self, instance, validated_data):
        new_tags = validated_data.pop("tags")
        new_ingredients = validated_data.pop("recipeingredient")

        instance.image = validated_data.get("image", instance.image)
        instance.name = validated_data.get("name", instance.name)
        instance.text = validated_data.get("text", instance.text)
        instance.cooking_time = validated_data.get(
            "cooking_time",
            instance.cooking_time
        )

        # Перезаписываем теги
        new_tags = set(tag.id for tag in new_tags)
        current_tags = set(instance.tags.values_list("id", flat=True))

        tags_to_delete = current_tags - new_tags
        if tags_to_delete:
            instance.tags.remove(*tags_to_delete)

        tags_to_add = new_tags - current_tags
        if tags_to_add:
            instance.tags.add(*tags_to_add)

        # Перезаписывам ингредиенты
        current_ingredients = {
            ing.ingredient_id: ing for ing in instance.recipeingredient.all()
        }
        new_ingredients = {ing["id"].id: ing for ing in new_ingredients}

        for ing_id in current_ingredients.keys():
            if ing_id not in new_ingredients:
                current_ingredients[ing_id].delete()
        
        new_ingredients_list = []
        for ing_id, data in new_ingredients.items():
            if ing_id in current_ingredients:
                current_ingredients[ing_id].amount = data["amount"]
                current_ingredients[ing_id].save()
            else:
                new_ingredients_list.append(
                    RecipeIngredient(
                        ingredient=ing_id,
                        amount=data["amount"],
                        recipe=instance,
                    )
                )
        if new_ingredients_list:
            RecipeIngredient.objects.bulk_create(new_ingredients_list)

        instance.save()
        return instance


class SubscriptionsRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для рецептом пользователя,
    на которого текущий пользователь подписался.
    """

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class SubscriptionsSerializer(UserSerializer):
    """
    Сериализатор для получение информации о пользователе,
    на которого текущий пользователь подписался.
    """

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    def get_recipes(self, obj):
        """Получаем рецепты пользователя."""
        # Получаем ограничение на количество рецептов из запроса
        recipes_limit = self.context.get("request").query_params.get(
            "recipes_limit", None
        )
        # Получаем нужное количество рецептов
        if recipes_limit:
            try:
                recipes_limit = int(recipes_limit)
                if recipes_limit < 1:
                    raise serializers.ValidationError(
                        "Значение recipes_limit должно быть > 0"
                    )
                recipes = obj.author_recipes.all()[:recipes_limit]
            except ValueError:
                raise serializers.ValidationError(
                    "Значение recipes_limit не является числом"
                )
        else:
            recipes = obj.author_recipes.all()
        serializer = SubscriptionsRecipeSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        """Получаем количество рецептов пользователя."""
        return obj.author_recipes.count()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "avatar",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )
