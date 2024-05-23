from django.contrib import admin

from url_shortener.models import ShortURL

admin.site.register(ShortURL)
