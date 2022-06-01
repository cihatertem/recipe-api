"""
Serializers for the Recipe API view.
"""
from rest_framework import serializers
from core.models import Recipe, Tag, Ingredient, User as CustomUser


class IngredientSerializer(serializers.ModelSerializer):
    """
    Serializer for ingretients.
    """
    class Meta:
        model = Ingredient
        fields = ('id', 'name')
        read_only_fields = ('id',)


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
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes',
                  'price', 'link', 'tags', 'ingredients']
        read_only_fields = ('id',)

    def _get_or_create_tags(self, tags, recipe: Recipe) -> None:
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

    def _get_or_create_ingredients(self, ingredients, recipe: Recipe) -> None:
        """
        Handle getting or creating ingredients as needed
        """
        auth_user: CustomUser = self.context['request'].user
        for ingredient in ingredients:
            ingredient_obj, created = Ingredient.objects.get_or_create(
                user=auth_user,
                **ingredient
            )
            recipe.ingredients.add(ingredient_obj)

    def create(self, validated_data: dict) -> Recipe:
        # https://www.django-rest-framework.org/api-guide/serializers/#saving-instances
        """
        Create recipe.
        """
        tags: list = validated_data.pop('tags', [])
        ingredients: list = validated_data.pop('ingredients', [])
        recipe: Recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_tags(tags, recipe)
        self._get_or_create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance: Recipe, validated_data: dict) -> Recipe:
        """
        Update recipe.
        """
        # https://www.django-rest-framework.org/api-guide/serializers/#saving-instances
        tags: list | None = validated_data.pop('tags', None)
        ingredients: list | None = validated_data.pop('ingredients', None)

        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        if ingredients is not None:
            instance.ingredients.clear()
            self._get_or_create_ingredients(ingredients, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class RecipeDetailSerializer(RecipeSerializer):
    """
    Serializer for the recipe detail view.
    """
    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description', 'image']


class RecipeImageSerializer(serializers.ModelSerializer):
    """
    Serializer for uploading images to recipes.
    """
    class Meta:
        model = Recipe
        fields = ('id', 'image')
        read_only_fields = ('id',)
        extra_kwargs = {
            'image': {'required': 'True'}
        }
