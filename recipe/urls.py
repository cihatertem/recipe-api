"""
URL mappins for Recipe API.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from recipe import views

app_name: str = 'recipe'

router: DefaultRouter = DefaultRouter(trailing_slash=False)
router.register('recipes', views.RecipeViewSet)

urlpatterns: list = [
    path('', include(router.urls)),
]
