"""
Tests for Tag API endpoint actions.
"""
from decimal import Decimal

from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.response import Response

from core import models
from recipe.serializers import TagSerializer
from utils import helpers

TAGS_URL = reverse("recipe:tag-list")


class PublicTagsApiTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self) -> None:
        """Setup for test client"""
        self.client = APIClient()

    def test_auth_required(self) -> None:
        """Test auth is required for retrieving tags list."""
        response: Response = self.client.get(TAGS_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Test authenticated API requests"""

    def setUp(self) -> None:
        """Setup for authenticated user and test client."""
        self.user: models.User = helpers.create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self) -> None:
        """Test retrieving a list of tags."""
        helpers.create_tag(user=self.user, name="tag1")
        helpers.create_tag(user=self.user, name="tag2")
        helpers.create_tag(user=self.user, name="tag3")

        tags = models.Tag.objects.all()
        tags_count = tags.count()
        response: Response = self.client.get(TAGS_URL)
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(tags_count, 3)
        self.assertEqual(serializer.data, response.data)

    def test_tags_limited_to_owner_user(self) -> None:
        """Test list of tags is limited to autheticated users."""
        other_user: models.User = helpers.create_user(
            email="other_user@example.com",
            password="testpass123"
        )
        helpers.create_tag(
            user=other_user,
            name="Other user tag"
        )
        first_user_tag = helpers.create_tag(
            user=self.user,
            name="First user tag"
        )
        response: Response = self.client.get(TAGS_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], first_user_tag.name)
        self.assertEqual(response.data[0]["id"], str(first_user_tag.id))

    def test_tag_update_action(self) -> None:
        """Test updating a tag."""
        tag: models.Tag = helpers.create_tag(
            user=self.user,
            name="Dessert"
        )
        payload = {
            "name": "Fruity"
        }
        tag_detail_url = helpers.tag_detail_url(tag.id)
        response: Response = self.client.put(tag_detail_url, data=payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        tag.refresh_from_db()

        self.assertEqual(tag.name, payload["name"])

    def test_tag_delete_action(self) -> None:
        """Test deleting a tag."""
        tag: models.Tag = helpers.create_tag(
            user=self.user,
            name="Dessert"
        )
        tag_detail_url = helpers.tag_detail_url(tag.id)
        response: Response = self.client.delete(tag_detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        tag_exists: bool = models.Tag.objects.filter(id=tag.id).exists()

        self.assertFalse(tag_exists)

    def test_tag_delete_action_only_owner_user(self) -> None:
        """Test deleting a tag by only its owner user."""
        other_user: models.User = helpers.create_user(
            email="other_user@example.com",
            password="testpass123"
        )

        tag: models.Tag = helpers.create_tag(
            user=other_user,
            name="Dessert"
        )
        tag_detail_url = helpers.tag_detail_url(tag.id)
        response: Response = self.client.delete(tag_detail_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        tag_exists: bool = models.Tag.objects.filter(id=tag.id).exists()

        self.assertTrue(tag_exists)

    def test_filter_tags_assigned_to_recipes(self) -> None:
        """Test listing tags by thos assigned to recipes."""
        tag_one: models.Ingredient = helpers.create_tag(
            user=self.user,
            name="Apple"
        )
        tag_two: models.Ingredient = helpers.create_tag(
            user=self.user,
            name="Turkey"
        )
        recipe: models.Recipe = helpers.create_recipe(
            title="Apple Crumble",
            time_minutes=5,
            price=Decimal("4.55"),
            user=self.user
        )
        recipe.tags.add(tag_one)
        response: Response = self.client.get(
            TAGS_URL,
            {"assigned_only": 1}
        )
        serializer_one = TagSerializer(tag_one)
        serializer_two = TagSerializer(tag_two)

        self.assertIn(serializer_one.data, response.data)
        self.assertNotIn(serializer_two.data, response.data)

    def test_filtered_tags_unique(self) -> None:
        """Test filtered tags return a unique/distinct list."""
        tag_one: models.Ingredient = helpers.create_tag(
            user=self.user,
            name="Apple"
        )
        helpers.create_tag(
            user=self.user,
            name="Turkey"
        )
        recipe_one: models.Recipe = helpers.create_recipe(
            title="Apple Crumble",
            time_minutes=5,
            price=Decimal("4.55"),
            user=self.user
        )
        recipe_two: models.Recipe = helpers.create_recipe(
            title="Orange Crumble",
            time_minutes=15,
            price=Decimal("14.55"),
            user=self.user
        )
        recipe_one.tags.add(tag_one)
        recipe_two.tags.add(tag_one)
        response: Response = self.client.get(
            TAGS_URL,
            {"assigned_only": 1}
        )

        self.assertEqual(len(response.data), 1)
