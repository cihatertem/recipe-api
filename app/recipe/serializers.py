"""
Serializers for Recipe APIs.
"""
from rest_framework import serializers

from core.models import Recipe


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""
    class Meta:
        model = Recipe
        fields = (
            "id", "title", "description", "time_minutes", "price", "link",
            "created_at", "updated_at"
        )

        read_only_fields = ("id",)
