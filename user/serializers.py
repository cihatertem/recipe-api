"""
Serializers for the user API view.
"""
from django.contrib.auth import get_user_model, authenticate
from core.models import User as CustomUserModel
from rest_framework import serializers
from django.utils.translation import gettext as _


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the user object.
    """
    class Meta:
        model: CustomUserModel = get_user_model()
        fields: tuple = ('email', 'password', 'name')
        extra_kwargs: dict = {
            'password': {'write_only': True, 'min_length': 8}
        }

    def create(self, validated_data) -> CustomUserModel:
        """
        Create and return a user with encrypted password.
        """
        User: CustomUserModel = get_user_model()
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data) -> CustomUserModel:
        """
        Update and return an updated user.
        """
        password: str = validated_data.pop('password', None)
        user: CustomUserModel = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """
    Serializer for the user auth token.
    """
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        """
        Validate and authenticate the user.
        """
        email: str = attrs.get('email')
        password: str = attrs.get('password')
        user: CustomUserModel = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )

        if not user:
            msg: str = _('Unable to authenticate with provided credentials.')
            raise serializers.ValidationError(msg, code='authorization')
        attrs['user'] = user
        return attrs
