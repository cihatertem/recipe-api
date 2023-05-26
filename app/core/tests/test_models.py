"""
Tests for django models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User


class ModelTests(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an emain is successful.
        Default Django User model needs username to create a new user."""
        email = "test@test.com"
        password = "unsecure123"

        user: User = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
