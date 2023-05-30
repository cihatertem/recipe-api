"""
Tests for Tag API endpoint actions.
"""
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.response import Response

from core.models import Tag, User
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
        self.user: User = helpers.create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self) -> None:
        """Test retrieving a list of tags."""
        helpers.create_tag(user=self.user, name="tag1")
        helpers.create_tag(user=self.user, name="tag2")
        helpers.create_tag(user=self.user, name="tag3")

        tags = Tag.objects.all()
        tags_count = tags.count()
        response: Response = self.client.get(TAGS_URL)
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(tags_count, 3)
        self.assertEqual(serializer.data, response.data)

    def test_tags_limited_to_owner_user(self) -> None:
        """Test list of tags is limited to autheticated users."""
        other_user: User = helpers.create_user(
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
        self.assertEqual(response.data[0]["user"], first_user_tag.user.id)
