"""
Views for Recipe APIs.
"""
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request

from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
    TagSerializer,
    IngredientSerializer,
    RecipeImageSerializer)

from core.models import Recipe, Tag, Ingredient


class AuthenticationPermissionMixin:
    """Token auth and authentication requirement"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)


class BaseRecipeActionsViewSet(
    AuthenticationPermissionMixin,
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """Base viewset with action and auth/permission classes."""

    def get_queryset(self):
        "Filter and retrieve ingredients/tags for authenticated owner user."
        return self.queryset.filter(user=self.request.user).order_by("name")


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
        elif self.action == "upload_image":
            return RecipeImageSerializer

        return self.serializer_class

    @action(methods=["POST"], detail=True, url_path="upload-image")
    def upload_image(self, request: Request, pk=None) -> Response:
        """Upload an image to recipe."""
        recipe: Recipe = self.get_object()

        if recipe.image:
            recipe.image.delete()

        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(BaseRecipeActionsViewSet):
    """View for manage Tag APIs."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(BaseRecipeActionsViewSet):
    """View for manage Ingredient APIs"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
