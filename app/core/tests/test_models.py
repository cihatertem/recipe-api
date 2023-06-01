"""
Tests for django models.
"""
from unittest.mock import patch, MagicMock

from django.test import TestCase
from django.contrib.auth import get_user_model

from decimal import Decimal

from core import models
from utils import helpers


class ModelTests(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self) -> None:
        """Test creating a user with an email is successful.
        Default Django User model needs username to create a new user."""
        email = "test@test.com"
        password = "unsecure123"

        user: models.User = get_user_model().objects.create_user(email,
                                                                 password)

        self.assertTrue(user.is_active)
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_normalize_new_user_email(self) -> None:
        """Test email is normalized for new users."""
        emails = (
            ("test1@EXAMPLE.com", "test1@example.com"),
            ("Test2@Example.com", "Test2@example.com"),
            ("TEST3@EXAMPLE.com", "TEST3@example.com"),
            ("test4@example.COM", "test4@example.com"),
            ("  test5@example.com  ", "test5@example.com")
        )

        for email, expected in emails:
            user: models.User = get_user_model().objects.create_user(
                email,
                "testpass123"
            )

            self.assertEqual(user.email, expected)

    def test_email_required(self) -> None:
        """Test that creating a user without en email reaises a ValueError"""

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user("", "testpass123")

    def test_create_superuser(self) -> None:
        """Test creating a super user with an email is successful."""
        email = "test@test.com"
        password = "unsecure123"

        user: models.User = get_user_model().objects.create_superuser(email,
                                                                      password)

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_create_recipe(self) -> None:
        """Test creating a recipe is successful."""
        user: models.User = get_user_model().objects.create_user(
            "test@example.com",
            "testpass123"
        )

        recipe: models.Recipe = models.Recipe.objects.create(
            user=user,
            title="Test recipe",
            time_minutes=5,
            price=Decimal("5.50"),
            description="Test recipe description."
        )

        self.assertEqual(str(recipe), recipe.title)

    def test_create_tag(self) -> None:
        """Test creating a tag is successfull."""
        user: models.User = helpers.create_user(
            email="test@example.com",
            password="testpass123"
        )
        tag = models.Tag.objects.create(
            user=user,
            name="Test",
        )

        self.assertEqual(str(tag), tag.name)

    def test_create_ingredient(self) -> None:
        """Test creating an ingredient is successful."""
        user: models.User = helpers.create_user()
        ingredient: models.Ingredient = helpers.create_ingredient(
            user=user,
            name="Salt"
        )

        self.assertEqual(str(ingredient), ingredient.name)

    @patch("core.models.uuid.uuid4")
    def test_recipe_file_name_uuid(self, mock_uuid: MagicMock) -> None:
        """Test generating image path."""
        uuid = "test-uuid"
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, "example.jpg")

        self.assertEqual(file_path, f"uploads/recipe/{uuid}.jpg")
