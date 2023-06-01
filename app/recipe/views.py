"""
Views for Recipe APIs.
"""
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter
)
from drf_spectacular.types import OpenApiTypes

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


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                "assigned_only",
                OpenApiTypes.INT, enum=[0, 1],
                description="Filter by items assigned to recipes."
            )
        ]
    )
)
class BaseRecipeActionsViewSet(
    AuthenticationPermissionMixin,
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """Base viewset with action and auth/permission classes."""

    def get_queryset(self):
        """Filter and retrieve ingredients/tags by assigned recipes for
        authenticated owner user."""
        assigned_only: bool = bool(
            int(self.request.query_params.get("assigned_only", 0))
        )
        queryset = self.queryset

        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False)

        return queryset.filter(user=self.request.user)\
            .order_by("name").distinct()


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                "tags",
                OpenApiTypes.STR,
                description="Comma separated list of tags IDs to filter"
            ),
            OpenApiParameter(
                "ingredients",
                OpenApiTypes.STR,
                description="Comma separated list of ingredients IDs to filter"
            )
        ]
    )
)
class RecipeViewSet(AuthenticationPermissionMixin, viewsets.ModelViewSet):
    """View for manage Recipe APIs."""
    serializer_class = RecipeDetailSerializer
    queryset = Recipe.objects.all()

    def _params_to_list(self, queryset: str) -> list[str]:
        """Create and return a list of id strings"""
        return [idx.strip() for idx in queryset.split(",")]

    def get_queryset(self):
        """Filter and retrieve recipes by tags/ingredients for
        authenticated users."""
        tags = self.request.query_params.get("tags")
        ingredients = self.request.query_params.get("ingredients")
        queryset = self.queryset

        if tags:
            tags_ids = self._params_to_list(tags)
            queryset = queryset.filter(tags__id__in=tags_ids)

        if ingredients:
            ingredients_ids = self._params_to_list(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredients_ids)

        return queryset.filter(user=self.request.user)\
            .order_by("-created_at").distinct()

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
