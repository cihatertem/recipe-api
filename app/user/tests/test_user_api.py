"""Tests for User API"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import User
from utils.helpers import create_user

from rest_framework.response import Response


CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:token")
ME_URL = reverse("user:me")


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

    def test_create_token_for_user(self) -> None:
        "Test generates token for valid credentials."
        user_details = {
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
            "password": "testpass123"
        }

        create_user(**user_details)

        payload_to_token_endpoint = {
            "email": user_details["email"],
            "password": user_details["password"]
        }

        response: Response = self.client.post(
            TOKEN_URL,
            data=payload_to_token_endpoint
        )

        self.assertIn("token", response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self) -> None:
        """Test returns error if credentials invalid."""
        create_user(email="test@example.com",
                    password="goodpass123",
                    first_name="Test",
                    last_name="User")

        payload = {
            "email": "test@example.com",
            "password": "badpass123"
        }

        response: Response = self.client.post(TOKEN_URL, data=payload)

        self.assertNotIn("token", response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self) -> None:
        """Test posting a blank password returns an error."""
        payload = {
            "email": "test@example.com",
            "password": ""
        }

        response: Response = self.client.post(TOKEN_URL, data=payload)

        self.assertNotIn("token", response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self) -> None:
        """Test authentication is required for users."""
        response: Response = self.client.get(ME_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    class PrivateUserApiTests(TestCase):
        """Test User Api requests that require auhtentication."""

        def setUp(self) -> None:
            self.user = create_user(email="test@example.com",
                                    password="testpass123",
                                    first_name="Test",
                                    last_name="User")

            self.client = APIClient()
            self.client.force_authenticate(user=self.user)

        def test_retrieve_profile_success(self) -> None:
            """Test retrieving profile for logged in user."""
            response: Response = self.client.get(ME_URL)

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data,
                             {
                                 "email": self.user.email,
                                 "first_name": self.user.first_name,
                                 "last_name": self.user.last_name
                             })

        def test_post_me_not_allowed(self) -> None:
            """Test POST is not allowed for the me endpoint."""
            response: Response = self.client.post(ME_URL, {})

            self.assertEqual(response.status_code,
                             status.HTTP_405_METHOD_NOT_ALLOWED)

        def test_update_user_profile(self) -> None:
            """Test updating the user profile for the authenticated user."""
            payload = {
                "first_name": "Updated Test",
                "password": "updatedtestpass123"
            }

            response: Response = self.client.patch(ME_URL, data=payload)
            self.user.refresh_from_db()

            self.assertEqual(self.user.first_name, payload["first_name"])
            self.assertTrue(self.user.check_password(payload["password"]))
            self.assertEqual(response.status_code, status.HTTP_200_OK)
