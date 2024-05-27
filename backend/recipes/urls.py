from django.urls import path

from recipes import views

urlpatterns = [
    path('s/<str:uniq_id>/', views.expand),
]
