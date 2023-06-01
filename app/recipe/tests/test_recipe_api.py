"""
Tests for Recipe APIs.
"""
import os
import tempfile

from PIL import Image

from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.response import Response


from core import models
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


class PrivateRecipeApiTests(TestCase):
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

        recipes = models.Recipe.objects.all().order_by("-created_at")
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

        recipes = models.Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_get_recipe_detail(self) -> None:
        """Test get specific recipe detail with recipe ID."""
        recipe: models.Recipe = helpers.create_recipe(user=self.user)
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

        recipe: models.Recipe = models.Recipe.objects.get(
            id=response.data["id"])

        for key, value in payload.items():
            self.assertEqual(getattr(recipe, key), value)

        self.assertEqual(recipe.user, self.user)

    def test_partial_update_recipe(self) -> None:
        """Test partial update/patch action of recipe object."""
        original_link = "https://example.com/recipe"
        recipe: models.Recipe = helpers.create_recipe(
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
        recipe: models.Recipe = helpers.create_recipe(
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
        recipe: models.Recipe = helpers.create_recipe(
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
        recipe: models.Recipe = helpers.create_recipe(
            user=self.user,
            title="Test Recipe",
            description="Test description for Test Recipe.",
            price=Decimal("5.12"),
            link="https://example.com/recipe-test"
        )
        delete_endpoint = helpers.recipe_detail_url(recipe.id)
        response: Response = self.client.delete(delete_endpoint)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        recipe_exists: bool = models.Recipe.objects.filter(
            id=recipe.id).exists()

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

        other_user_recipe_exists: bool = models.Recipe.objects.filter(
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

        recipes = models.Recipe.objects.filter(
            user=self.user, title=payload["title"])

        self.assertEqual(recipes[0].tags.count(), 2)

        for tag in payload["tags"]:
            tag_is_exists: bool = recipes[0].tags.filter(
                name=tag["name"],
                user=self.user
            ).exists()

            self.assertTrue(tag_is_exists)

    def test_create_recipe_with_existing_tags(self) -> None:
        """Test creating a recipe with existing tags."""
        turkish_tag: models.Tag = helpers.create_tag(
            user=self.user, name="Turkish")
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

        recipes = models.Recipe.objects.filter(user=self.user)

        self.assertEqual(recipes.count(), 1)

        recipe: models.Recipe = recipes[0]

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
        recipe: models.Recipe = helpers.create_recipe(user=self.user)
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

        new_tag: models.Tag = models.Tag.objects.get(
            user=self.user, name="Launch")

        self.assertIn(new_tag, recipe.tags.all())

    def test_update_recipe_assign_tag(self) -> None:
        """Test assigning en existing tag when updating a recipe."""
        tag_breakfast: models.Tag = helpers.create_tag(
            user=self.user,
            name="Breakfast"
        )
        recipe: models.Recipe = helpers.create_recipe(
            user=self.user,
            title="Van Breakfast"
        )
        recipe.tags.add(tag_breakfast)

        tag_launch: models.Tag = helpers.create_tag(
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
        tag_one: models.Tag = helpers.create_tag(user=self.user, name="One")
        tag_two: models.Tag = helpers.create_tag(user=self.user, name="Two")
        recipe: models.Recipe = helpers.create_recipe(
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

    def test_create_recipe_with_new_ingredients(self) -> None:
        """Test creating a recipe with new ingredients."""
        payload = {
            "title": "Recipe with ingredients",
            "time_minutes": 60,
            "price": Decimal("15.67"),
            "ingredients": [
                {"name": "Coffee"},
                {"name": "Vanilla"}
            ]
        }
        response: Response = self.client.post(
            RECIPE_URL,
            data=payload,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        recipes = models.Recipe.objects.filter(user=self.user)

        self.assertEqual(recipes.count(), 1)
        self.assertEqual(recipes[0].ingredients.count(), 2)

        for ingredient in payload["ingredients"]:
            ingredient_is_exist: bool = recipes[0].ingredients.filter(
                name=ingredient["name"],
                user=self.user
            ).exists()

            self.assertTrue(ingredient_is_exist)

    def test_create_recipe_with_existing_ingredient(self) -> None:
        """Test creating a new reciper with existing ingredient."""
        ingredient: models.Ingredient = helpers.create_ingredient(
            user=self.user,
            name="Yogurt"
        )
        payload = {
            "title": "Recipe with yogurt",
            "time_minutes": 34,
            "price": Decimal("11.50"),
            "ingredients": [
                {"name": "Yogurt"},
                {"name": "Somon"}
            ],
            "tags": [
                {"name": "Sauce"}
            ]
        }

        response: Response = self.client.post(
            RECIPE_URL,
            data=payload,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        recipe: models.Recipe = models.Recipe.objects.filter(user=self.user)[0]

        self.assertEqual(recipe.ingredients.count(), 2)
        self.assertIn(ingredient, recipe.ingredients.all())

        for ingredient in payload["ingredients"]:
            ingredient_is_exist: bool = recipe.ingredients.filter(
                name=ingredient["name"],
                user=self.user
            ).exists()

            self.assertTrue(ingredient_is_exist)

    def test_create_ingredient_on_update(self) -> None:
        """Test creating and ingredient when updating a recipe."""
        recipe: models.Recipe = helpers.create_recipe(user=self.user)
        payload = {
            "ingredients": [
                {"name": "Tomato"}
            ]
        }
        recipe_detail_url = helpers.recipe_detail_url(recipe.id)
        response: Response = self.client.patch(
            recipe_detail_url,
            data=payload,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        new_ingredient: models.Ingredient = models.Ingredient.objects.get(
            user=self.user,
            name="Tomato"
        )

        self.assertIn(new_ingredient, recipe.ingredients.all())

    def test_update_recipe_assign_ingredient(self) -> None:
        """Test assinging an existing ingredient when updating a recipe."""
        ingredient_one: models.Ingredient = helpers.create_ingredient(
            user=self.user,
            name="Pepper"
        )
        recipe: models.Recipe = helpers.create_recipe(user=self.user)
        recipe.ingredients.add(ingredient_one)

        ingredient_two: models.Ingredient = helpers.create_ingredient(
            user=self.user,
            name="Chili"
        )
        payload = {
            "ingredients": [
                {"name": "Chili"}
            ]
        }
        recipe_detail_url = helpers.recipe_detail_url(recipe.id)
        response: Response = self.client.patch(
            recipe_detail_url,
            data=payload,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(ingredient_two, recipe.ingredients.all())
        self.assertNotIn(ingredient_one, recipe.ingredients.all())

    def test_clear_recipe_ingredients(self) -> None:
        """Test clearing a recipe's ingredients."""
        ingredient: models.Ingredient = helpers.create_ingredient(
            user=self.user,
            name="Garlic"
        )

        recipe: models.Recipe = helpers.create_recipe(user=self.user)
        recipe.ingredients.add(ingredient)
        payload = {"ingredients": []}
        recipe_detail_url = helpers.recipe_detail_url(recipe.id)
        response: Response = self.client.patch(
            recipe_detail_url,
            data=payload,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 0)

    def test_filter_by_tags(self) -> None:
        """Test filtering recipes by tags."""
        recipe_one: models.Recipe = helpers.create_recipe(
            user=self.user,
            title="Pudding"
        )
        recipe_two: models.Recipe = helpers.create_recipe(
            user=self.user,
            title="Tea"
        )
        recipe_three: models.Recipe = helpers.create_recipe(
            user=self.user,
            title="Fish&Chips"
        )
        tag_one: models.Tag = helpers.create_tag(
            user=self.user,
            name="Dessert"
        )
        tag_two: models.Tag = helpers.create_tag(
            user=self.user,
            name="Drink"
        )
        recipe_one.tags.add(tag_one)
        recipe_two.tags.add(tag_two)

        params = {
            "tags": f"{tag_one.id}, {tag_two.id}"
        }
        response: Response = self.client.get(RECIPE_URL, params)

        serializer_one = RecipeSerializer(recipe_one)
        serializer_two = RecipeSerializer(recipe_two)
        serializer_three = RecipeSerializer(recipe_three)

        self.assertIn(serializer_one.data, response.data)
        self.assertIn(serializer_two.data, response.data)
        self.assertNotIn(serializer_three.data, response.data)

    def test_filter_by_ingredients(self) -> None:
        """Test filtering recipes by ingredients."""
        recipe_one: models.Recipe = helpers.create_recipe(
            user=self.user,
            title="Pudding"
        )
        recipe_two: models.Recipe = helpers.create_recipe(
            user=self.user,
            title="Tea"
        )
        recipe_three: models.Recipe = helpers.create_recipe(
            user=self.user,
            title="Fish&Chips"
        )
        ingredient_one: models.Ingredient = helpers.create_ingredient(
            user=self.user,
            name="Cocoa"
        )
        ingredient_two: models.Ingredient = helpers.create_ingredient(
            user=self.user,
            name="Water"
        )
        recipe_one.ingredients.add(ingredient_one)
        recipe_two.ingredients.add(ingredient_two)
        params = {
            "ingredients": f"{ingredient_one.id}, {ingredient_two.id}"
        }
        response: Response = self.client.get(RECIPE_URL, params)
        serializer_one = RecipeSerializer(recipe_one)
        serializer_two = RecipeSerializer(recipe_two)
        serializer_three = RecipeSerializer(recipe_three)

        self.assertIn(serializer_one.data, response.data)
        self.assertIn(serializer_two.data, response.data)
        self.assertNotIn(serializer_three.data, response.data)


class ImageUploadTests(TestCase):
    """Tests for the image upload API."""

    def setUp(self) -> None:
        """Setup for test user and client."""
        self.client = APIClient()
        self.user = helpers.create_user()
        self.client.force_authenticate(self.user)
        self.recipe = helpers.create_recipe(user=self.user)

    def tearDown(self) -> None:
        """Logic runs after tests."""
        self.recipe.image.delete()

    def test_upload_image(self) -> None:
        """Test uploading an image to a recipe."""
        image_upload_url = helpers.image_upload_url(self.recipe.id)

        with tempfile.NamedTemporaryFile(suffix=".jpg") as image_file:
            image: Image.Image = Image.new("RGB", (10, 10))
            image.save(image_file, format="JPEG")
            image_file.seek(0)

            payload = {
                "image": image_file
            }
            response: Response = self.client.post(
                image_upload_url,
                data=payload,
                format="multipart"
            )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.recipe.refresh_from_db()

        self.assertIn("image", response.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self) -> None:
        """Test uploading invalid image."""
        image_upload_url = helpers.image_upload_url(self.recipe.id)
        payload = {
            "image": "notanimagefile"
        }
        response: Response = self.client.post(
            image_upload_url,
            data=payload,
            format="multipart"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
