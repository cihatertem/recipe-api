""""
Tests for the health check API.
"""
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.response import Response


class HealthCheckTests(TestCase):
    """Test the health check API."""

    def test_health_check(self) -> None:
        """Test health check API."""
        client = APIClient()
        endpoint = reverse("health-check")
        response: Response = client.get(endpoint)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
