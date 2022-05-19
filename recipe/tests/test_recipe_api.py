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
from core.models import Recipe, User as CustomUserModel
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer
from recipe.tests.utils import create_recipe, detail_url, create_user

RECIPES_URL: str = reverse('recipe:recipe-list')


class PublicRecipeAPITests(TestCase):
    """
    Test unauthenticated API requests.
    """

    def setUp(self) -> None:
        """
        Set tests' tools up.
        """
        self.client = APIClient()

    def test_auth_required(self) -> None:
        """
        Test auth is required to call API.
        """
        res: Response = self.client.get(RECIPES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):
    """
    Test authenticated API requests.
    """

    def setUp(self) -> None:
        """
        Set tests' tools up.
        """
        self.client = APIClient()
        self.User: CustomUserModel = get_user_model()
        self.user: CustomUserModel = create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self) -> None:
        """
        Test retrieving a list of recipes.
        """
        for _ in range(2):
            create_recipe(user=self.user)

        res: Response = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.all().order_by('-id')
        serializer: RecipeSerializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_list_limited_to_user(self) -> None:
        """
        Test list of recipes is limited to authenticated user.
        """
        other_user: CustomUserModel = create_user(
            email='otheruser@example.com',
            password='otherpass123'
        )

        create_recipe(user=other_user)
        create_recipe(user=self.user)

        res: Response = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.filter(user=self.user)
        serializer: RecipeSerializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self) -> None:
        """
        Test get recipe detail.
        """
        recipe: Recipe = create_recipe(user=self.user)
        url: str = detail_url(recipe.id)
        res: Response = self.client.get(url)
        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self) -> None:
        """
        Test creating a recipe.
        """
        payload: dict = {
            "title": 'Sample recipe',
            'time_minutes': 30,
            'price': Decimal('5.95')
        }

        res: Response = self.client.post(RECIPES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe: Recipe = Recipe.objects.get(id=res.data['id'])
        for k, v in payload.items():
            # https://docs.python.org/3/library/functions.html#getattr
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_partial_update(self) -> None:
        """
        Test partial update of a recipe.
        """
        orginal_link: str = 'https://example.com/recipe.pdf'
        recipe: Recipe = create_recipe(
            user=self.user,
            title='Sample recipe title',
            link=orginal_link
        )

        payload: dict = {
            'title': 'New recipe title'
        }
        url: str = detail_url(recipe.id)
        res: Response = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, orginal_link)
        self.assertEqual(recipe.user, self.user)

    def test_full_update(self) -> None:
        """
        Test full update of a recipe.
        """
        orginal_link: str = 'https://example.com/recipe.pdf'
        recipe: Recipe = create_recipe(
            user=self.user,
            title='Sample recipe title',
            link=orginal_link,
            description='Sample recipe description'
        )

        payload: dict = {
            'title': 'New recipe title',
            'link': 'https://example.com/new-recipe.pdf',
            'description': 'New recipe description',
            'time_minutes': 10,
            'price': Decimal('2.50')

        }
        url: str = detail_url(recipe.id)
        res: Response = self.client.put(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        recipe.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_update_user_returns_error(self) -> None:
        """
        Test changing the recipe user results in an error.
        """
        new_user: CustomUserModel = create_user(
            email='testuser2@example.com',
            password='testpass13'
        )
        recipe: Recipe = create_recipe(user=self.user)
        payload: dict = {'user': new_user.id}
        url: str = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self) -> None:
        """
        Test deleting a recipe successful.
        """
        recipe: Recipe = create_recipe(user=self.user)
        url: str = detail_url(recipe.id)
        res: Response = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_delete_recipe_other_users_recipe_error(self) -> None:
        """
        Test tyring to delete another users recipe gives error.
        """
        new_user: CustomUserModel = create_user(
            email='user2@example.com',
            password='testpass123'
        )
        recipe: Recipe = create_recipe(user=new_user)
        url: str = detail_url(recipe.id)
        res: Response = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())
