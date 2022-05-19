"""
Tools for Recipe Tests
"""
from django.urls import reverse
from decimal import Decimal
from core.models import Recipe, User as CustomUserModel
from django.contrib.auth import get_user_model


def create_recipe(user, **params) -> Recipe:
    """
    Create and return a sample recipe.
    """
    defaults: dict = {
        'title': ' Sample recipe title',
        'time_minutes': 22,
        'price': Decimal('5.25'),
        'description': 'Sample description.',
        'link': 'https://example.com/recipe.pdf'
    }

    defaults.update(params)
    recipe: Recipe = Recipe.objects.create(
        user=user,
        **defaults
    )

    return recipe


def detail_url(recipe_id) -> str:
    """
    Create and return a recipe detail URL.
    """
    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_user(**params) -> CustomUserModel:
    """
    Create and return a new user.
    """
    User: CustomUserModel = get_user_model()
    return User.objects.create_user(**params)
