"""
Serializers for Recipe APIs.
"""
from rest_framework import serializers

from core.models import Recipe


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""
    class Meta:
        model = Recipe
        fields = ["id", "title", "time_minutes", "price", "link"]

        read_only_fields = ["id"]

    def create(self, validated_data: dict):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail view."""
    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + \
            ["description", "created_at", "updated_at"]

        read_only_fields = RecipeSerializer.Meta.read_only_fields + \
            ["created_at", "updated_at"]
