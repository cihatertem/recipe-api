"""
Serializers for the User API View.
"""
from typing import Type
from django.contrib.auth import (
    get_user_model,
    authenticate
)
from django.utils.translation import gettext as _

from rest_framework import serializers

from core.models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    class Meta:
        model: Type[User] = get_user_model()
        fields = (
            "email",
            "password",
            "first_name",
            "middle_name",
            "last_name"
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

    def update(self, instance: User, validated_data: dict) -> User:
        """Update and return user."""
        password = validated_data.pop("password", None)
        user: User = super().update(instance, validated_data)

        if password is not None:
            user.set_password(password)  # encrypt/hash point
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token."""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={"input_type": "password"},
        trim_whitespace=False
    )

    def validate(self, attrs: dict) -> dict:
        """Validate and authenticate the user."""
        email = attrs.get("email")
        password = attrs.get("password")
        user: User | None = authenticate(
            request=self.context.get("request"),
            username=email,  # Custom User model changed username to email
            password=password
        )

        if user is None:
            message = _("Uanble to authenticate with provided credentials.")

            raise serializers.ValidationError(message, code="authorization")

        attrs["user"] = user

        return attrs
