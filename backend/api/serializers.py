from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import Ingredient
from users.constants import PASSWORD_MAX_LENGTH

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователей."""

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'avatar')


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)


class IngredientSerialiser(serializers.ModelSerializer):
    """Сериализатор для ингридиентов."""

    class Meta:
        model = Ingredient
        fields = '__all__'
