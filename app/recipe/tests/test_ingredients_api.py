"""
Tests for ingredients APIs.
"""
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.response import Response

from core import models
from utils import helpers
from recipe.serializers import IngredientSerializer


INGREDIENTS_URL = reverse("recipe:ingredient-list")


class PublicIngredientsApiTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self) -> None:
        """Setup for test client."""
        self.client = APIClient()

    def test_auth_required(self) -> None:
        """Test auth is requred for retrievind ingredients."""
        response: Response = self.client.get(INGREDIENTS_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self) -> None:
        """Setup for test client and authenticated test user."""
        self.client = APIClient()
        self.user: models.User = helpers.create_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self) -> None:
        """Test retrieving a list of ingredients."""
        helpers.create_ingredient(
            user=self.user,
            name="Salt"
        )
        helpers.create_ingredient(
            user=self.user,
            name="Cherry"
        )
        response: Response = self.client.get(INGREDIENTS_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        ingredients = models.Ingredient.objects.all().order_by("name")
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(response.data, serializer.data)

    def test_ingredients_limited_to_request_authenticated_owner(self) -> None:
        """Test list of ingredients is limited to authenticated owner user."""
        other_user: models.User = helpers.create_user(
            email="other@example.com",
            password="testpass123"
        )
        helpers.create_ingredient(
            user=other_user,
            name="Water"
        )
        ingredient: models.Ingredient = helpers.create_ingredient(
            user=self.user,
            name="Red Hot Chilli Pepper"
        )
        response: Response = self.client.get(INGREDIENTS_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], ingredient.name)
        self.assertEqual(response.data[0]["id"], str(ingredient.id))

    def test_put_update_ingredient(self) -> None:
        """Test updating an ingredient with put method"""
        ingredient: models.Ingredient = helpers.create_ingredient(
            user=self.user,
            name="Salt"
        )
        payload = {
            "name": "Sugar"
        }
        ingredient_detail_endpoint = helpers.ingredient_detail_url(
            ingredient.id
        )
        response: Response = self.client.put(
            ingredient_detail_endpoint,
            data=payload,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        ingredient.refresh_from_db()

        self.assertEqual(ingredient.name, payload["name"])

    def test_patch_update_ingredient(self) -> None:
        """Test updating an ingredient with patch method"""
        ingredient: models.Ingredient = helpers.create_ingredient(
            user=self.user,
            name="Salt"
        )
        payload = {
            "name": "Sugar"
        }
        ingredient_detail_endpoint = helpers.ingredient_detail_url(
            ingredient.id
        )
        response: Response = self.client.patch(
            ingredient_detail_endpoint,
            data=payload,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        ingredient.refresh_from_db()

        self.assertEqual(ingredient.name, payload["name"])

    def test_delete_ingredient(self) -> None:
        """Test deleting an ingredient."""
        ingredient: models.Ingredient = helpers.create_ingredient(
            user=self.user,
            name="Salt"
        )
        ingredient_detail_endpoint = helpers.ingredient_detail_url(
            ingredient.id
        )
        response: Response = self.client.delete(
            ingredient_detail_endpoint,
            data={}
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        ingredient_is_exist: bool = models.Ingredient.objects.filter(
            user=self.user,
            id=ingredient.id
        ).exists()

        self.assertFalse(ingredient_is_exist)
