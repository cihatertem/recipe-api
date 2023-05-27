"""
Tests for the Django admin modifications.
"""

from django.http import HttpResponse
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from core.models import User


class AdminSiteTests(TestCase):
    """Tests for Django admin."""

    def setUp(self) -> None:
        """Create user and Client for test setup."""
        self.client = Client()
        self.admin_user: User = get_user_model().objects.create_superuser(
            email="admin@example.com",
            password="testpass123"
        )

        self.client.force_login(self.admin_user)

        self.user: User = get_user_model().objects.create_user(
            email="user@example.com",
            password="testpass123",
            first_name="Cihat"
        )

    def test_users_list(self):
        """Test that users are listed on page."""
        # https://docs.djangoproject.com/en/4.2/ref/contrib/admin
        # /#reversing-admin-urls
        url = reverse("admin:core_user_changelist")

        response = self.client.get(url)

        self.assertContains(response, self.user.first_name)
        self.assertContains(response, self.user.email)

    def test_edit_user_page(self):
        """Test the admin user edit page works."""
        url = reverse("admin:core_user_change", args=(self.user.id,))
        response: HttpResponse = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_add_user_page(self):
        """Test the admin page's add user section works"""
        url = reverse("admin:core_user_add")
        response: HttpResponse = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_delete_user_page(self):
        """Test the admin page's delete user section works."""
        url = reverse("admin:core_user_delete", args=(self.user.id,))
        response: HttpResponse = self.client.post(
            url,
            data={"name": "post",
                  "value": "yes"}
        )
        user: User | bool = User.objects.filter(pk=self.user.id).exists()

        self.assertEqual(response.status_code, 302)
        self.assertFalse(user)
