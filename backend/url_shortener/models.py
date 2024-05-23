from django.db import models

from url_shortener.constants import URL_MAX_LENGTH


class ShortURL(models.Model):
    """Модель для коротких ссылок."""

    full_url = models.URLField("Полный URL", max_length=URL_MAX_LENGTH)
    uniq_id = models.CharField(
        "Уникальный идентификатор",
        max_length=URL_MAX_LENGTH
    )

    class Meta:
        verbose_name = "короткая ссылка"
        verbose_name_plural = "Короткие ссылки"

    def __str__(self) -> str:
        return self.full_url
