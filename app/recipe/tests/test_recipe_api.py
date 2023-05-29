"""
Tests for Recipe APIs.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.response import Response


from core.models import Recipe, User
from recipe.serializers import RecipeSerializer


RECIPE_URL = reverse("recipe:recipe-list")


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


class PublicRecipeApiTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self) -> None:
        """Client setup for requests' tests."""
        self.client = APIClient()

    def test_authentication_required(self) -> None:
        """Test auth is required to call API."""
        response: Response = self.client.get(RECIPE_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateReciperApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self) -> None:
        """Client and authenticated user setup for requests' tests."""

        self.client = APIClient()
        self.user: User = get_user_model().objects.create_user(
            "test@example.com",
            "testpass123"
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self) -> None:
        """Test retrieving a list of recipes"""
        create_recipe(user=self.user)
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        response: Response = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all().order_by("-created_at")
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, response.data)

    def test_recipe_list_limited_to_authenticated_request_user(self) -> None:
        other_user = get_user_model().objects.create_user(
            "other@example.com",
            "testpass123"
        )

        create_recipe(user=other_user)
        create_recipe(user=self.user)

        response: Response = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
