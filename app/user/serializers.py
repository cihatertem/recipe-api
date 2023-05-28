"""
Serializers for the User API View.
"""
from typing import Type
from django.contrib.auth import get_user_model

from rest_framework import serializers

from core.models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    class Meta:
        model: Type[User] = get_user_model()
        fields = (
            "email", "password", "first_name", "middle_name", "last_name"
        )
        extra_kwargs = {
            "password": {
                "write_only": True,  # does not return encrypted user password
                "min_length": 8
            }
        }

    def create(self, validated_data) -> User:
        """Create and return a user with encrypted password."""
        return get_user_model().objects.create_user(**validated_data)
