"""
Tests for the ingredients API.
"""
from django.test import TestCase
from django.db.models import QuerySet
from rest_framework.reverse import reverse
from rest_framework.authentication import get_user_model
from rest_framework.response import Response
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Ingredient, User as CustomUser
from recipe.serializers import IngredientSerializer
from recipe.tests.utils import (
    create_user, create_ingredient, ingredient_detail_url
)

INGREDIENTS_URL = reverse('recipe:ingredient-list')


class PublicIngredientsApiTests(TestCase):
    """
    Test unauthenticated API requests.
    """

    def setUp(self) -> None:
        """
        Test set up.
        """
        self.client: APIClient = APIClient()
        return super().setUp()

    def test_auth_required(self) -> None:
        """
        Test auth is required for retrieving ingredients.
        """
        res: Response = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """
    Test authenticated API requests.
    """

    def setUp(self) -> None:
        """
        Test set up.
        """
        self.user: CustomUser = create_user()
        self.client: APIClient = APIClient()
        self.client.force_authenticate(user=self.user)
        return super().setUp()

    def test_retrieve_ingredients(self) -> None:
        """
        Test retrieving a list of ingredients.
        """
        create_ingredient(self.user, 'Kale')
        create_ingredient(self.user, 'Vanilla')
        res: Response = self.client.get(INGREDIENTS_URL)

        ingredients: QuerySet[Ingredient] = Ingredient.objects.all().order_by(
            '-name')
        serializer: IngredientSerializer = IngredientSerializer(
            ingredients,
            many=True
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_request_user(self) -> None:
        """
        Test list of ingredients is limited to autheticated request user.
        """
        user2: CustomUser = create_user(email='user2@example.com')
        create_ingredient(user=user2, name='Salt')
        ingredient: Ingredient = create_ingredient(
            user=self.user,
            name='Pepper'
        )
        res: Response = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)
        self.assertEqual(res.data[0]['id'], str(ingredient.id))

    def test_update_ingredient(self) -> None:
        """
        Test updating an ingredient.
        """
        ingredient: Ingredient = create_ingredient(self.user, 'Cilantro')
        payload: dict = {
            'name': 'Coriander'
        }
        url: str = ingredient_detail_url(ingredient.id)
        res: Response = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload['name'])

    def test_delete_ingredient(self) -> None:
        """
        Test deleting ingredient.
        """
        ingredient: Ingredient = create_ingredient(self.user, 'Lettuce')
        url: str = ingredient_detail_url(ingredient.id)
        res: Response = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        ingredients: QuerySet[Ingredient] = Ingredient.objects.filter(
            user=self.user)
        self.assertFalse(ingredients.exists())
