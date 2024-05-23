import random
import string

from django.conf import settings


def generate_short_code(length=settings.SHORT_CODE_LENGTH):
    """Генератор уникальных кодов"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))
