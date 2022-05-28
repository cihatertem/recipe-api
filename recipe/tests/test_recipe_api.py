"""
Tests for Recipe APIs.
"""
from decimal import Decimal
from genericpath import exists
from hashlib import new
from unicodedata import name
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.db.models import QuerySet
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.response import Response
from core.models import Recipe, Tag, Ingredient, User as CustomUserModel
import recipe
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer
from recipe.tests.utils import (
    create_recipe,
    detail_url,
    create_user,
    create_tag,
    create_ingredient
)

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
        recipes: QuerySet[Recipe] = Recipe.objects.all().order_by('-id')
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
        recipes: QuerySet[Recipe] = Recipe.objects.filter(user=self.user)
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

    def test_create_recipe_with_new_tags(self):
        """
        Test creating a recipe with new tags.
        """
        payload: dict = {
            'title': 'Tahi Prawn Curry',
            'time_minutes': 30,
            'price': Decimal('2.50'),
            'tags': [
                {'name': 'Thai'},
                {'name': 'Dinner'}
            ]
        }
        res: Response = self.client.post(
            RECIPES_URL,
            payload,
            format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes: QuerySet[Recipe] = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe: Recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        for tag in payload['tags']:
            exists: bool = recipe.tags.filter(
                name=tag['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_tags(self):
        """
        Test creating a recipe with existing tag.
        """
        tag_indian: Tag = create_tag(user=self.user, name='Indian')
        payload: dict = {
            'title': 'Pongal',
            'time_minutes': 60,
            'price': Decimal('4.50'),
            'tags': [
                {'name': 'Indian'},
                {'name': 'Breakfast'}
            ]
        }
        res: Response = self.client.post(
            RECIPES_URL,
            payload,
            format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes: QuerySet[Recipe] = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe: Recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(tag_indian, recipe.tags.all())
        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_tag_on_update(self):
        """
        Test creating tag when updating a recipe.
        """
        recipe: Recipe = create_recipe(user=self.user)
        payload: dict = {'tags': [{'name': 'Launch'}]}
        url: str = detail_url(recipe.id)
        res: Response = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag: Tag = Tag.objects.get(user=self.user, name='Launch')
        self.assertIn(new_tag, recipe.tags.all())

    def test_update_assign_tag(self):
        """
        Test assigning an existing tag when updating a recipe.
        """
        tag_breakfast: Tag = create_tag(self.user, 'Breakfast')
        recipe: Recipe = create_recipe(self.user)
        recipe.tags.add(tag_breakfast)

        tag_launch: Tag = create_tag(self.user, 'Launch')
        payload: dict = {
            'tags': [{'name': 'Launch'}]
        }
        url: str = detail_url(recipe.id)
        res: Response = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_launch, recipe.tags.all())
        self.assertNotIn(tag_breakfast, recipe.tags.all())

    def test_clear_recipe_tags(self):
        """
        Test clearing a recipes tags.
        """
        tag: Tag = create_tag(self.user, 'Dessert')
        recipe: Recipe = create_recipe(self.user)
        recipe.tags.add(tag)
        payload: dict = {
            'tags': []
        }
        url: str = detail_url(recipe.id)
        res: Response = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)

    def test_recipe_with_new_ingredients(self) -> None:
        """
        Test creating a recipe with new ingredients.
        """
        payload: dict = {
            'title': 'Cauliflower Taco',
            'time_minutes': 60,
            'price': Decimal('4.30'),
            'ingredients': [
                {'name': 'Cauliflower'},
                {'name': 'Salt'}
            ]
        }
        res: Response = self.client.post(RECIPES_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipes: QuerySet[Recipe] = Recipe.objects.filter(user=self.user)
        recipe: Recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)

        for ingredient in payload['ingredients']:
            exists: bool = recipe.ingredients.filter(
                name=ingredient['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_ingredient(self) -> None:
        """
        Test creating a new recipe with existing ingredient.
        """
        ingredient: Ingredient = create_ingredient(self.user, 'Lemon')
        payload: dict = {
            'title': 'Vietnamese Soup',
            'time_minutes': 25,
            'price': Decimal('2.55'),
            'ingredients': [
                {'name': 'Lemon'},
                {'name': 'Fish Sauce'}
            ]
        }
        res: Response = self.client.post(RECIPES_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipes: QuerySet[Recipe] = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)

        recipe: Recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)
        self.assertIn(ingredient, recipe.ingredients.all())

        for ingredient in payload['ingredients']:
            exists: bool = recipe.ingredients.filter(
                name=ingredient['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_ingredient_on_update(self) -> None:
        """
        Test creating an ingredient when updating a recipe.
        """
        recipe: Recipe = create_recipe(self.user)
        payload: dict = {
            'ingredients': [
                {'name': 'Limes'}
            ]
        }
        url: str = detail_url(recipe.id)
        res: Response = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        new_ingredient: Ingredient = Ingredient.objects.get(
            user=self.user,
            name='Limes'
        )
        self.assertIn(new_ingredient, recipe.ingredients.all())

    def test_update_recipe_assing_ingredient(self) -> None:
        """
        Test assinging an existing ingredient when updating a recipe.
        """
        ingredient1: Ingredient = create_ingredient(self.user, 'Pepper')
        recipe: Recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient1)

        ingredient2: Ingredient = create_ingredient(self.user, 'Chili')
        payload: dict = {
            'ingredients': [
                {'name': 'Chili'}
            ]
        }
        url: str = detail_url(recipe.id)
        res: Response = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(ingredient2, recipe.ingredients.all())
        self.assertNotIn(ingredient1, recipe.ingredients.all())

    def test_clearing_recipe_ingredients(self) -> None:
        """
        Test clearing a recipe's ingredients.
        """
        ingredient: Ingredient = create_ingredient(self.user, 'Garlic')
        recipe: Recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient)
        payload: dict = {'ingredients': []}
        url: str = detail_url(recipe.id)
        res: Response = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 0)
