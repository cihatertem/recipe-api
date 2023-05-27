"""
Tests for django models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User


class ModelTests(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful.
        Default Django User model needs username to create a new user."""
        email = "test@test.com"
        password = "unsecure123"

        user: User = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertTrue(user.is_active)
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_normalize_new_user_email(self):
        """Test email is normalized for new users."""
        emails = (
            ("test1@EXAMPLE.com", "test1@example.com"),
            ("Test2@Example.com", "Test2@example.com"),
            ("TEST3@EXAMPLE.com", "TEST3@example.com"),
            ("test4@example.COM", "test4@example.com"),
            ("  test5@example.com  ", "test5@example.com")
        )

        for email, expected in emails:
            user: User = get_user_model().objects.create_user(
                email, "testpass123"
            )

            self.assertEqual(user.email, expected)

    def test_email_required(self):
        """Test that creating a user without en email reaises a ValueError"""

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user("", "testpass123")

    def test_create_superuser(self):
        """Test creating a super user with an email is successful."""
        email = "test@test.com"
        password = "unsecure123"

        user: User = get_user_model().objects.create_superuser(
            email=email,
            password=password
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
