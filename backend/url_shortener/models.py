from django.db import models

class ShortURL(models.Model):
    full_url = models.URLField("Полный URL", max_length=200)
    uniq_id = models.CharField("Уникальный идентификатор", max_length=200)
