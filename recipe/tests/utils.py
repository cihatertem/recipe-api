"""
Tools for Recipe Tests
"""
from django.urls import reverse
from decimal import Decimal
from core.models import Ingredient, Recipe, Tag, User as CustomUser
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


# def create_user(**params) -> CustomUser:
#     """
#     Create and return a new user.
#     """
#     User: CustomUser = get_user_model()
#     return User.objects.create_user(**params)

def create_user(
    email: str = 'user@example.com',
    password: str = 'testpassw123',
    **extra_fields
) -> CustomUser:
    """
    Create and return a new user.
    """
    User: CustomUser = get_user_model()
    return User.objects.create_user(
        email=email,
        password=password,
        **extra_fields
    )


def create_tag(user: CustomUser, name: str) -> None:
    """
    Create and return a tag.
    """
    return Tag.objects.create(user=user, name=name)


def tag_detail_url(tag_id: str) -> str:
    """
    Create and return a tag detail url.
    """
    return reverse('recipe:tag-detail', args=[tag_id])


def create_ingredient(user: CustomUser, name: str) -> Ingredient:
    """
    Create and return an ingredient.
    """
    return Ingredient.objects.create(user=user, name=name)


def ingredient_detail_url(ingredient_id: str) -> str:
    """
    Create and return an ingredient detail url.
    """
    return reverse('recipe:ingredient-detail', args=[ingredient_id])
