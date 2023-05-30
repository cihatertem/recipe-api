"""
Serializers for Recipe APIs.
"""
from rest_framework import serializers

from core.models import Recipe, Tag


class TagSerializer(serializers.ModelSerializer):
    """Serializer for the tags"""
    class Meta:
        model = Tag
        fields = "__all__"
        read_only_fields = ["id", "user", "created_at", "updated_at"]


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ["id", "title", "time_minutes", "price", "link", "tags"]
        read_only_fields = ["id"]

    def create(self, validated_data: dict):
        """Create a recipe."""
        validated_data["user"] = self.context["request"].user
        tags = validated_data.pop("tags", [])
        recipe: Recipe = Recipe.objects.create(**validated_data)

        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=validated_data["user"],
                **tag
            )
            recipe.tags.add(tag_obj)

        return recipe


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail view."""
    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + \
            ["description", "created_at", "updated_at"]
        read_only_fields = RecipeSerializer.Meta.read_only_fields + \
            ["created_at", "updated_at"]
