"""
Serializers for Recipe APIs.
"""
from rest_framework import serializers

from core.models import Recipe, Tag, User, Ingredient


class TagSerializer(serializers.ModelSerializer):
    """Serializer for the tags"""
    class Meta:
        model = Tag
        fields = ["id", "name"]
        read_only_fields = ["id"]


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for the ingredients."""
    class Meta:
        model = Ingredient
        fields = ["id", "name"]
        read_only_fields = ["id"]


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""
    tags = TagSerializer(many=True, required=False)
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = [
            "id", "title", "time_minutes", "price", "link", "tags",
            "ingredients", "image"
        ]
        read_only_fields = ["id", "image"]

    def create(self, validated_data: dict) -> Recipe:
        """Create a recipe with creation and adding tags."""
        validated_data["user"] = self.context["request"].user
        tags = validated_data.pop("tags", [])
        ingredients = validated_data.pop("ingredients", [])
        recipe: Recipe = Recipe.objects.create(**validated_data)

        self._get_or_create_ingredients(
            user=validated_data["user"],
            ingredients=ingredients,
            recipe=recipe
        )

        self._get_or_create_tags(
            user=validated_data["user"],
            tags=tags,
            recipe=recipe
        )

        return recipe

    def update(self, instance: Recipe, validated_data: dict) -> Recipe:
        """Update a recipe with creation, adding, clearing tags."""
        tags = validated_data.pop("tags", None)
        ingredients = validated_data.pop("ingredients", None)
        request_user: User = self.context["request"].user

        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(
                user=request_user,
                tags=tags,
                recipe=instance)

        if ingredients is not None:
            instance.ingredients.clear()
            self._get_or_create_ingredients(
                user=request_user,
                ingredients=ingredients,
                recipe=instance
            )

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        return instance

    def _get_or_create_tags(
            self,
            user: User,
            tags: list[Tag],
            recipe: Recipe
    ) -> None:
        """Handle getting or creating tags as needed."""
        for tag in tags:
            existing_tag, created = Tag.objects.get_or_create(
                user=user,
                **tag,
            )

            recipe.tags.add(existing_tag)

    def _get_or_create_ingredients(
            self,
            user: User,
            ingredients: list[Ingredient],
            recipe: Recipe
    ) -> None:
        """Handle getting or creating ingredients as needed."""
        for ingredient in ingredients:
            existing_ingredient, created = Ingredient.objects.get_or_create(
                user=user,
                **ingredient,
            )

            recipe.ingredients.add(existing_ingredient)


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail view."""
    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + \
            ["description", "created_at", "updated_at"]
        read_only_fields = RecipeSerializer.Meta.read_only_fields + \
            ["created_at", "updated_at"]


class RecipeImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to recipes."""
    class Meta:
        model = Recipe
        fields = ["id", "image"]
        read_only_fields = ["id"]
        extra_kwargs = {
            "image": {"required": True}
        }
