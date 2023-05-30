"""
Helper functions for operations.
"""
from django.urls import reverse
from django.contrib.auth import get_user_model

from decimal import Decimal

from core.models import Recipe, Tag, User, Ingredient


def recipe_detail_url(recipe_id) -> str:
    """Create and return a recipe detail URL."""
    return reverse("recipe:recipe-detail", args=(recipe_id,))


def tag_detail_url(tag_id) -> str:
    """Create and return a tag detail URL."""
    return reverse("recipe:tag-detail", args=(tag_id,))


def ingredient_detail_url(ingredient_id) -> str:
    """Create and return a ingredient detail URL."""
    return reverse("recipe:ingredient-detail", args=(ingredient_id,))


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


def create_user(
        email="test@example.com", password="testpass123", **params
) -> User:
    """Create and return a new user."""
    return get_user_model().objects.create_user(
        email=email,
        password=password,
        **params
    )


def create_tag(user: User, name: str) -> Tag:
    """Create and return a tag."""
    return Tag.objects.create(user=user, name=name)


def create_ingredient(user: User, name: str) -> Tag:
    """Create and return an ingredient."""
    return Ingredient.objects.create(user=user, name=name)
