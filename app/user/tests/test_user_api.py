"""Tests for User API"""
from typing import Any
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import User

from rest_framework.request import HttpRequest  # noqa
from rest_framework.response import Response


CREATE_USER_URL = reverse("user:create")


def create_user(**params: Any) -> User:
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the public features of the user API."""

    def setUp(self) -> None:
        """Setup test case."""
        self.client = APIClient()

    def test_create_user_success(self) -> None:
        """Test creating a user is successful."""
        payload = {
            "email": "test@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User"
        }

        response: Response = self.client.post(CREATE_USER_URL, data=payload)
        user: User = get_user_model().objects.get(email=payload["email"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(user.check_password(payload["password"]))
        # hashed or plain text password should never return back.
        self.assertNotIn("password", response.data)

    def test_user_with_email_exists_error(self) -> None:
        """Test error returned if user with email exists."""
        payload = {
            "email": "test@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User"
        }

        create_user(**payload)
        response: Response = self.client.post(CREATE_USER_URL, data=payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_with_too_short_error(self) -> None:
        """Test an error if returned if password less than 5 chars."""
        payload = {
            "email": "test@example.com",
            "password": "test",
            "first_name": "Test",
            "last_name": "User"
        }

        response: Response = self.client.post(CREATE_USER_URL, data=payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        user_is_exists: bool = get_user_model().objects.filter(
            email=payload["email"]
        ).exists()

        self.assertFalse(user_is_exists)
