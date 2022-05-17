"""
Tests for models.
"""
from django.test import TestCase
# https://docs.djangoproject.com/en/3.2/topics/auth/customizing/#django.contrib.auth.get_user_model
from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    """
    Test Models.
    """

    def test_create_user_with_email_successful(self) -> None:
        """
        Test creating a user with an email is successful.
        """
        User = get_user_model()
        email: str = 'test@example.com'
        password: str = 'abcdef123'
        user: User = User.objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        # https://docs.djangoproject.com/en/3.2/topics/auth/customizing/#django.contrib.auth.models.AbstractBaseUser.check_password
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self) -> None:
        """
        Test email is normalized for new users.
        """
        sample_email: list = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
            ['test5@example.com ', 'test5@example.com'],
            [' test6@example.com', 'test6@example.com'],
        ]

        for email, expected_email in sample_email:
            User = get_user_model()
            user: User = User.objects.create_user(email, 'testpass123')
            self.assertEqual(user.email, expected_email)

    def test_new_user_without_email_raises_error(self) -> None:
        """
        Test that creating a user without an email
        raises a ValueError
        """
        with self.assertRaises(ValueError):
            User = get_user_model()
            User.objects.create_user('', 'testpass123')

    def test_create_superuser(self) -> None:
        """
        Test creating a superuser.
        """
        User = get_user_model()
        user: User = User.objects.create_superuser(
            email='test@example.com',
            password='testpass123'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
