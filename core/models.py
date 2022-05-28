"""
Database models.
"""
from django.db import models
from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
)
from uuid import uuid4
from core.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """
    Customized User Model in the System.
    """
    id = models.UUIDField(
        default=uuid4,
        unique=True,
        primary_key=True,
        editable=False
    )
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects: UserManager = UserManager()
    USERNAME_FIELD: str = 'email'


class Recipe(models.Model):
    """
    Recipe object.
    """
    id = models.UUIDField(
        default=uuid4,
        unique=True,
        primary_key=True,
        editable=False
    )
    # https://stackoverflow.com/questions/24629705/django-using-get-user-model-vs-settings-auth-user-model
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField(blank=True)
    link = models.CharField(max_length=255, blank=True)
    tags = models.ManyToManyField('Tag')
    ingredients = models.ManyToManyField('Ingredient')

    def __str__(self) -> str:
        return str(self.title)


class Tag(models.Model):
    """
    Tag for filtering recipes.
    """
    id = models.UUIDField(
        default=uuid4,
        unique=True,
        primary_key=True,
        editable=False
    )
    name = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, related_name='tags')

    def __str__(self) -> str:
        return self.name[:25]


class Ingredient(models.Model):
    """
    Ingredient for recipes.
    """
    id = models.UUIDField(
        default=uuid4,
        unique=True,
        primary_key=True,
        editable=False
    )
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ingredients'
    )

    def __str__(self) -> str:
        return self.name
