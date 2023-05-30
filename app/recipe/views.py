"""
Views for Recipe APIs.
"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
    TagSerializer)

from core.models import Recipe, Tag


class AuthenticationPermissionMixin:
    """Token auth and authentication requirement"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)


class RecipeViewSet(AuthenticationPermissionMixin, viewsets.ModelViewSet):
    """View for manage Recipe APIs."""
    serializer_class = RecipeDetailSerializer
    queryset = Recipe.objects.all()

    def get_queryset(self):
        """Retrieve recipes for authenticated users."""
        return self.queryset.filter(user=self.request.user)\
            .order_by("-created_at")

    def get_serializer_class(self):
        """Change and return the serializer class for request."""
        if self.action == "list":
            return RecipeSerializer

        return self.serializer_class


class TagViewSet(AuthenticationPermissionMixin, viewsets.ModelViewSet):
    """View for manage Tag APIs."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    def get_queryset(self):
        """Retriev tags for authenticated owner users."""
        return self.queryset.filter(user=self.request.user)\
            .order_by("name")
