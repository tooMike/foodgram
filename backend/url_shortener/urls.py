from django.urls import path

from url_shortener import views

urlpatterns = [
    path('<str:uniq_id>/', views.expand),
]
