"""
Helper functions for operations.
"""
from django.urls import reverse
from django.contrib.auth import get_user_model

from decimal import Decimal

from core.models import Recipe, User


def recipe_detail_url(recipe_id) -> str:
    """Create and return a recipe detail URL."""
    return reverse("recipe:recipe-detail", args=(recipe_id,))


def create_recipe(user: User, **params: dict) -> Recipe:
    """Create and return a recipe object."""
    defaults = {
        "title": "Test Recipe",
        "description": "Tasty test recipe.",
        "price": Decimal("5.25"),
        "time_minutes": 22,
        "link": "https:example.com/test_recipe"
    }

    defaults.update(params)
    recipe: Recipe = Recipe.objects.create(user=user, **defaults)

    return recipe


def create_user(**params) -> User:
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)
