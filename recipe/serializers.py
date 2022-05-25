"""
Serializers for the Recipe API view.
"""
from rest_framework import serializers
from core.models import Recipe, Tag, User as CustomUser


class TagSerializer(serializers.ModelSerializer):
    """
    Serializer for tags.
    """
    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)


class RecipeSerializer(serializers.ModelSerializer):
    """
    Serializer for the recipe object.
    """
    # https://www.django-rest-framework.org/api-guide/relations/#nested-relationships
    # https://www.django-rest-framework.org/api-guide/relations/#writable-nested-serializers
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link', 'tags']
        read_only_fields = ('id',)

    def _get_or_create_tags(self, tags: Tag, recipe: Recipe) -> None:
        """
        Handle getting or creating tags as needed
        """
        auth_user: CustomUser = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag
            )
            recipe.tags.add(tag_obj)

    def create(self, validated_data: dict) -> Recipe:
        # https://www.django-rest-framework.org/api-guide/serializers/#saving-instances
        """
        Create recipe.
        """
        tags: list = validated_data.pop('tags', [])
        recipe: Recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_tags(tags, recipe)
        return recipe

    def update(self, instance: Recipe, validated_data: dict) -> Recipe:
        """
        Update recipe.
        """
        # https://www.django-rest-framework.org/api-guide/serializers/#saving-instances
        tags: list | None = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class RecipeDetailSerializer(RecipeSerializer):
    """
    Serializer for the recipe detail view.
    """
    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']
