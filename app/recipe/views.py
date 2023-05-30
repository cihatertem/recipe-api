"""
Views for Recipe APIs.
"""
from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
    TagSerializer,
    IngredientSerializer)

from core.models import Recipe, Tag, Ingredient


class AuthenticationPermissionMixin:
    """Token auth and authentication requirement"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)


class RecipeViewSet(AuthenticationPermissionMixin, viewsets.ModelViewSet):
    """View for manage Recipe APIs."""
    serializer_class = RecipeDetailSerializer
    queryset = Recipe.objects.all()

    def get_queryset(self):
        """Filter and retrieve recipes for authenticated users."""
        return self.queryset.filter(user=self.request.user)\
            .order_by("-created_at")

    def get_serializer_class(self):
        """Change and return the serializer class for request."""
        if self.action == "list":
            return RecipeSerializer

        return self.serializer_class


class TagViewSet(
        AuthenticationPermissionMixin,
        mixins.DestroyModelMixin,
        mixins.UpdateModelMixin,
        mixins.ListModelMixin,
        viewsets.GenericViewSet
):
    """View for manage Tag APIs."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    def get_queryset(self):
        """Filter and retrieve tags for authenticated owner user."""
        return self.queryset.filter(user=self.request.user).order_by("name")


class IngredientViewSet(
    AuthenticationPermissionMixin,
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """View for manage Ingredient APIs"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

    def get_queryset(self):
        "Filter and retrieve ingredients for authenticated owner user."
        return self.queryset.filter(user=self.request.user).order_by("name")
