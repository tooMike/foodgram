from django.db import models


class ShortURL(models.Model):
    """Модель для коротких ссылок."""
    
    full_url = models.URLField("Полный URL", max_length=200)
    uniq_id = models.CharField("Уникальный идентификатор", max_length=200)

    class Meta:
        verbose_name = "короткая ссылка"
        verbose_name_plural = "Короткие ссылки"

    def __str__(self) -> str:
        return self.full_url
