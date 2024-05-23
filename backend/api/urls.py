from django.urls import include, path
from rest_framework import routers

from api import views as api_views

app_name = "api"

router_v1 = routers.DefaultRouter()
router_v1.register(
    "ingredients",
    api_views.IngredientViewSet,
    basename="ingredients"
)
router_v1.register("tags", api_views.TagViewSet, basename="tags")
router_v1.register("users", api_views.UserViewSet, basename="users")
router_v1.register("recipes", api_views.RecipeViewSet, basename="recipes")


urlpatterns = [
    path("", include(router_v1.urls)),
    path("auth/", include("djoser.urls.authtoken")),
]
