"""
Tests for models.
"""
from django.test import TestCase
# https://docs.djangoproject.com/en/3.2/topics/auth/customizing/#django.contrib.auth.get_user_model
from django.contrib.auth import get_user_model
from core.models import (
    User as CustomUser,
    Recipe,
    Tag,
    Ingredient,
    recipe_image_file_path
)
from core.tests.utils import create_user
from decimal import Decimal
from unittest.mock import patch
from uuid import UUID


class ModelTests(TestCase):
    """
    Test Models.
    """
    User: CustomUser = get_user_model()

    def test_create_user_with_email_successful(self) -> None:
        """
        Test creating a user with an email is successful.
        """
        email: str = 'test@example.com'
        password: str = 'abcdef123'
        user: CustomUser = self.User.objects.create_user(
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
            user: CustomUser = self.User.objects.create_user(
                email=email,
                password='testpass123'
            )
            self.assertEqual(user.email, expected_email)

    def test_new_user_without_email_raises_error(self) -> None:
        """
        Test that creating a user without an email
        raises a ValueError
        """
        with self.assertRaises(ValueError):
            self.User.objects.create_user('', 'testpass123')

    def test_create_superuser(self) -> None:
        """
        Test creating a superuser.
        """
        user: CustomUser = self.User.objects.create_superuser(
            email='test@example.com',
            password='testpass123'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe(self) -> None:
        """
        Test creating a recipe is successful.
        """
        user: CustomUser = self.User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )

        recipe: Recipe = Recipe.objects.create(
            user=user,
            title='Sample recipe name',
            time_minutes=5,
            price=Decimal('5.50'),
            description='Sample recipe description'
        )

        self.assertEqual(str(recipe), recipe.title)

    def test_create_tag(self) -> None:
        """
        Test creating a tag is successful.
        """
        user: CustomUser = create_user()
        tag: Tag = Tag.objects.create(user=user, name='Tag')
        self.assertEqual(str(tag), tag.name)

    def test_create_ingredient(self) -> None:
        """
        Test creating an ingredient successful.
        """
        user: CustomUser = create_user()
        ingredient: Ingredient = Ingredient.objects.create(
            user=user,
            name='Ingredient1'
        )

        self.assertEqual(str(ingredient), ingredient.name)

    @patch('core.models.uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid: UUID):
        """
        Test genering image path.
        """
        uuid: str = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path: str = recipe_image_file_path(None, 'example.jpg')

        self.assertEqual(file_path, f'uploads/recipe/{uuid}.jpg')
