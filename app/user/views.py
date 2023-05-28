"""
Views for User API.
"""
from rest_framework import generics

from user.serializers import UserSerializer


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system endpoint."""
    serializer_class = UserSerializer
