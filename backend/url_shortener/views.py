from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect

from url_shortener.models import ShortURL


def expand(request, uniq_id):
    """Представление для коротких ссылок."""
    try:
        link = get_object_or_404(ShortURL, uniq_id=uniq_id).full_url
        return redirect(link)
    except Exception as e:
        return HttpResponse(e.args)
