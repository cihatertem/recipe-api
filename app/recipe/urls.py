"""
URL mappings for Recipe APIs.
"""
from django.urls import path, include

from rest_framework.routers import DefaultRouter

from recipe import views

app_name = "recipe"

router = DefaultRouter(trailing_slash=False)
router.register("/recipes", viewset=views.RecipeViewSet)
router.register("/tags", viewset=views.TagViewSet)
router.register("/ingredients", viewset=views.IngredientViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
