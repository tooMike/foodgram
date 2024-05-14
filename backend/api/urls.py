from django.urls import include, path
from rest_framework import routers

from api import views


app_name = "api"

router_v1 = routers.DefaultRouter()
router_v1.register('ingredients', views.IngredientViewSet, basename='ingredients')
# router_v1.register('users', views.UserViewSet, basename='users')


urlpatterns = [
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path(
        'users/me/avatar/',
        views.AvatarViewSet.as_view({
            'patch': 'partial_update',
            'delete': 'destroy'
        }),
        name='avatar')
]
