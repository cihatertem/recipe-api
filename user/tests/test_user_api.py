"""
Tests for the user API.
"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from core.models import User as CustomUserModel
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.response import Response
from user.tests.utils import create_user


CREATE_USER_URL = reverse('user:create')
TOKEN_LOGIN_URL = reverse('user:login')
ME_URL = reverse('user:me')


class PublicUserApiTests(TestCase):
    """
    Test public features of user API.
    """

    def setUp(self) -> None:
        """
        Pre-settings for testing.
        """
        self.client = APIClient()

    def test_create_user_success(self) -> None:
        """
        Test creating a user is successful.
        """
        User: CustomUserModel = get_user_model()
        payload: dict = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test User'
        }
        res: Response = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        user: CustomUserModel = User.objects.get(
            email=payload['email']
        )
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_with_email_exists_error(self) -> None:
        """
        Test error returned if user with email exists.
        """
        payload: dict = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test User'
        }
        create_user(**payload)
        res: Response = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self) -> None:
        """
        Test an error is returned if password less than 8 chars.
        """
        User: CustomUserModel = get_user_model()
        payload: dict = {
            'email': 'test@example.com',
            'password': '1234',
            'name': 'Test User'
        }
        res: Response = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        is_user_exist: bool = User.objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(is_user_exist)

    def test_create_token_for_user(self) -> None:
        """
        Test generates token for valid credentials.
        """
        user_details: dict = {
            'name': 'Test Name',
            'email': 'test@example.com',
            'password': 'testpass123'
        }

        create_user(**user_details)
        payload: dict = {
            'email': user_details['email'],
            'password': user_details['password']
        }
        res: Response = self.client.post(TOKEN_LOGIN_URL, payload)
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self) -> None:
        """
        Test returns error if credentials invalid.
        """
        user_details: dict = {
            'name': 'Test Name',
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        create_user(**user_details)

        payload: dict = {
            'email': 'test@example.com',
            'password': 'wrongpass'
        }
        res: Response = self.client.post(TOKEN_LOGIN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self) -> None:
        """
        Test posting a blank password returns an error.
        """
        user_details: dict = {
            'name': 'Test Name',
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        create_user(**user_details)

        payload: dict = {
            'email': 'test@example.com',
            'password': ''
        }
        res: Response = self.client.post(TOKEN_LOGIN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retreive_user_unauthorized(self) -> None:
        """
        Test authentication is required for users.
        """
        res: Response = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """
    Tests API requests that require authentication.
    """

    def setUp(self) -> None:
        self.user: CustomUserModel = create_user(
            email='test@example.com',
            password='testpass123',
            name='Test User'
        )
        self.client: APIClient = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retreive_profile_success(self) -> None:
        """
        Test retrieving profile for logged in user.
        """
        res: Response = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'email': self.user.email,
            'name': self.user.name
        })

    def test_post_me_not_allowed(self) -> None:
        """
        Test post is not allowed for me endpoint.
        """
        res: Response = self.client.post(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self) -> None:
        """
        Test updating the user profile for the authenticated user.
        """
        payload: dict = {
            'name': 'Updated User Name',
            'password': 'newpass123'
        }
        res: Response = self.client.patch(ME_URL, payload)
        # https://docs.djangoproject.com/en/4.0/ref/models/instances/#django.db.models.Model.refresh_from_db
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
