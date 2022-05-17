"""
Tests for the Django Admin Modifications.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.http.response import HttpResponse


class AdminSiteTest(TestCase):
    """
    Tests for Django admin.
    """

    def setUp(self) -> None:
        """
        Create user and client.
        """
        # https://docs.djangoproject.com/en/3.2/topics/testing/tools/#overview-and-a-quick-example
        self.client = Client()
        User = get_user_model()
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='testpass123'
        )
        self.client.force_login(self.admin_user)
        self.user = User.objects.create_user(
            email='user@example.com',
            password='testpass123',
            name='Test User'
        )

    def test_users_list(self) -> None:
        """
        Test that users are listed on page.
        """
        # https://docs.djangoproject.com/en/3.2/ref/contrib/admin/#reversing-admin-urls
        url: str = reverse('admin:core_user_changelist')
        response: HttpResponse = self.client.get(url)
        self.assertContains(response, self.user.name)
        self.assertContains(response, self.user.email)

    def test_edit_user_page(self) -> None:
        """
        Test the edit user page works.
        """
        url: str = reverse('admin:core_user_change', args=[self.user.id])
        response: HttpResponse = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_create_user_page(self) -> None:
        """
        Test the create user page works.
        """
        url: str = reverse('admin:core_user_add')
        response: HttpResponse = self.client.get(url)
        self.assertEqual(response.status_code, 200)
