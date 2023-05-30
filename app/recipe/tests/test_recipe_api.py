"""
Tests for Recipe APIs.
"""
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.response import Response


from core.models import Recipe, Tag
from utils import helpers
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


RECIPE_URL = reverse("recipe:recipe-list")


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
        self.user = helpers.create_user()

        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self) -> None:
        """Test retrieving a list of recipes"""
        helpers.create_recipe(user=self.user)
        helpers.create_recipe(user=self.user)
        helpers.create_recipe(user=self.user)

        response: Response = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all().order_by("-created_at")
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, response.data)

    def test_recipe_list_limited_to_authenticated_request_user(self) -> None:
        other_user = helpers.create_user(
            email="other@example.com",
            password="testpass123"
        )

        helpers.create_recipe(user=other_user)
        helpers.create_recipe(user=self.user)

        response: Response = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_get_recipe_detail(self) -> None:
        """Test get specific recipe detail with recipe ID."""
        recipe: Recipe = helpers.create_recipe(user=self.user)
        url = helpers.recipe_detail_url(recipe.id)
        response: Response = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe, many=False)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_recipe(self) -> None:
        """Test creating a recipe object."""
        payload = {
            "title": "Test Recipe 2",
            "description": "Test tasty recipe",
            "time_minutes": 30,
            "price": Decimal("5.99"),
            "link": "https://example.com/test-recipe-2"
        }

        response: Response = self.client.post(RECIPE_URL, data=payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        recipe: Recipe = Recipe.objects.get(id=response.data["id"])

        for key, value in payload.items():
            self.assertEqual(getattr(recipe, key), value)

        self.assertEqual(recipe.user, self.user)

    def test_partial_update_recipe(self) -> None:
        """Test partial update/patch action of recipe object."""
        original_link = "https://example.com/recipe"
        recipe: Recipe = helpers.create_recipe(
            user=self.user,
            title="Test Recipe",
            link=original_link
        )
        payload = {"title": "Test Recipe Updated"}
        api_endpoint = helpers.recipe_detail_url(recipe.id)
        response: Response = self.client.patch(api_endpoint, data=payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        recipe.refresh_from_db()

        self.assertEqual(recipe.title, payload["title"])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

    def test_full_update_recipe(self) -> None:
        """Test full update / put action of a recipe object."""
        recipe: Recipe = helpers.create_recipe(
            user=self.user,
            title="Test Recipe",
            description="Test description for Test Recipe.",
            price=Decimal("5.12"),
            link="https://example.com/recipe-test"
        )
        payload = {
            "title": "Recipe Title Updated",
            "time_minutes": 23,
            "link": "https://example.com/recipe-test-updated",
            "description": "Test description for Test Recipe.",
            "price": Decimal("5.12"),
        }
        put_endpoint = helpers.recipe_detail_url(recipe.id)

        response: Response = self.client.put(put_endpoint, data=payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        recipe.refresh_from_db()

        for key, value in payload.items():
            self.assertEqual(getattr(recipe, key), value)
        self.assertEqual(recipe.user, self.user)

    def test_update_recipe_user_returns_error(self) -> None:
        """Test update recipe user should return an error."""
        recipe: Recipe = helpers.create_recipe(
            user=self.user,
            title="Test Recipe",
            description="Test description for Test Recipe.",
            price=Decimal("5.12"),
            link="https://example.com/recipe-test"
        )
        new_user = helpers.create_user(email="new_user@example.com",
                                       password="testpass123")

        payload = {"user": new_user}
        patch_endpoint = helpers.recipe_detail_url(recipe.id)
        self.client.patch(patch_endpoint, data=payload)

        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self) -> None:
        """Test delete action for a recipe object."""
        recipe: Recipe = helpers.create_recipe(
            user=self.user,
            title="Test Recipe",
            description="Test description for Test Recipe.",
            price=Decimal("5.12"),
            link="https://example.com/recipe-test"
        )
        delete_endpoint = helpers.recipe_detail_url(recipe.id)
        response: Response = self.client.delete(delete_endpoint)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        recipe_exists: bool = Recipe.objects.filter(id=recipe.id).exists()

        self.assertFalse(recipe_exists)

    def test_delete_recipe_other_users_error(self) -> None:
        """Test trying to delete another users' recipes gives error."""
        other_user = helpers.create_user(
            email="other_user@example.com",
            password="testpass123"
        )
        other_user_recipe = helpers.create_recipe(
            user=other_user,
            title="Other User's Recipe"
        )
        recipe_endpoint = helpers.recipe_detail_url(other_user_recipe.id)
        response: Response = self.client.delete(recipe_endpoint)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        other_user_recipe_exists: bool = Recipe.objects.filter(
            id=other_user_recipe.id
        ).exists()

        self.assertTrue(other_user_recipe_exists)

    def test_create_recipe_with_new_tags(self) -> None:
        """Test creating a recipe with new tags."""
        payload = {
            "title": "Thai Pai Chicken",
            "time_minutes": "30",
            "price": Decimal("2.50"),
            "tags": [
                {"name": "Thai"},
                {"name": "Dinner"}
            ]
        }
        response: Response = self.client.post(
            RECIPE_URL,
            data=payload,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        recipes = Recipe.objects.filter(user=self.user, title=payload["title"])

        self.assertEqual(recipes[0].tags.count(), 2)

        for tag in payload["tags"]:
            tag_is_exists: bool = recipes[0].tags.filter(
                name=tag["name"],
                user=self.user
            ).exists()

            self.assertTrue(tag_is_exists)

    def test_create_recipe_with_existing_tags(self) -> None:
        """Test creating a recipe with existing tags."""
        turkish_tag: Tag = helpers.create_tag(user=self.user, name="Turkish")
        payload = {
            "title": "Imam Bayildi",
            "time_minutes": 50,
            "price": Decimal("20.70"),
            "tags": [
                {"name": "Turkish"},
                {"name": "Aubergine"}
            ]
        }
        reponse: Response = self.client.post(
            RECIPE_URL,
            data=payload,
            format="json"
        )

        self.assertEqual(reponse.status_code, status.HTTP_201_CREATED)

        recipes = Recipe.objects.filter(user=self.user)

        self.assertEqual(recipes.count(), 1)

        recipe: Recipe = recipes[0]

        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(turkish_tag, recipe.tags.all())

        for tag in payload["tags"]:
            tag_is_exists: bool = recipe.tags.filter(
                user=self.user,
                name=tag["name"]
            ).exists()

            self.assertTrue(tag_is_exists)

    def test_create_tag_on_recipe_update(self) -> None:
        """Test creating tag when updating a recipe."""
        recipe: Recipe = helpers.create_recipe(user=self.user)
        payload = {
            "tags": [
                {"name": "Launch"}
            ]
        }
        recipe_detail_url = helpers.recipe_detail_url(recipe.id)
        response: Response = self.client.patch(
            recipe_detail_url,
            data=payload,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(payload["tags"][0]["name"], recipe.tags.all()[0].name)

        new_tag: Tag = Tag.objects.get(user=self.user, name="Launch")

        self.assertIn(new_tag, recipe.tags.all())

    def test_update_recipe_assign_tag(self) -> None:
        """Test assigning en existing tag when updating a recipe."""
        tag_breakfast: Tag = helpers.create_tag(
            user=self.user,
            name="Breakfast"
        )
        recipe: Recipe = helpers.create_recipe(
            user=self.user,
            title="Van Breakfast"
        )
        recipe.tags.add(tag_breakfast)

        tag_launch: Tag = helpers.create_tag(
            user=self.user,
            name="Launch"
        )
        payload = {
            "tags": [
                {"name": "Launch"}
            ]
        }
        recipe_detail_url = helpers.recipe_detail_url(recipe.id)
        response: Response = self.client.patch(
            recipe_detail_url,
            data=payload,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(tag_launch, recipe.tags.all())
        self.assertEqual(recipe.tags.all().count(), 1)
        self.assertNotIn(tag_breakfast, recipe.tags.all())

    def test_clear_recipe_tags(self) -> None:
        """Test clearing a recipe's tags."""
        tag_one: Tag = helpers.create_tag(user=self.user, name="One")
        tag_two: Tag = helpers.create_tag(user=self.user, name="Two")
        recipe: Recipe = helpers.create_recipe(
            user=self.user,
            title="Super Testy Recipe"
        )
        recipe.tags.add(tag_one, tag_two)
        payload = {
            "tags": []
        }
        recipe_detail_url = helpers.recipe_detail_url(recipe.id)

        response: Response = self.client.patch(
            recipe_detail_url,
            data=payload,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)
