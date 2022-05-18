"""
Helper functions for tests.
"""
from django.contrib.auth import get_user_model
from core.models import User as CustomUserModel


def create_user(**params) -> CustomUserModel:
    """
    Create and return a new user.
    """
    User: CustomUserModel = get_user_model()
    return User.objects.create_user(**params)
