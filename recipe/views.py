"""
Views for Recipe APIs.
"""
from ast import match_case
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer
from core.models import Recipe


class RecipeViewSet(viewsets.ModelViewSet):
    """
    View for manage recipe APIs.
    """
    serializer_class = RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """
        Retrieve recipes for authenticated user.
        """
        return self.queryset.filter(user=self.request.user).order_by('-id')

    # https://www.django-rest-framework.org/api-guide/generic-views/#get_serializer_classself
    def get_serializer_class(self):
        """
        Return the serializer class for request.
        """
        if self.action == 'list':
            return RecipeSerializer
        return self.serializer_class

    # https://www.django-rest-framework.org/api-guide/generic-views/#get_serializer_classself
    # Save and deletion hooks:
    def perform_create(self, serializer):
        """
        Create a new recipe.
        """
        serializer.save(user=self.request.user)
