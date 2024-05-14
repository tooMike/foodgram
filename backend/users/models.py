from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from users.constants import NAMES_MAX_LENGTH


class FoodgramUser(AbstractUser):
    """Модель пользователя."""

    # Делаем поля модели обязательными
    first_name = models.CharField(_('first name'), max_length=NAMES_MAX_LENGTH)
    last_name = models.CharField(_('last name'), max_length=NAMES_MAX_LENGTH)
    email = models.EmailField(_('email address'), unique=True)
    avatar = models.ImageField(_('avatar'), upload_to='users', blank=True)
    subscriptions = models.ManyToManyField(
        'self', verbose_name='Подписки',
        related_name='user',
        symmetrical=False
    )
    REQUIRED_FIELDS = ('first_name', 'last_name', 'email')

    def get_absolute_url(self):
        return reverse("users:profile")
    
    class Meta:
        ordering = ('id',)
