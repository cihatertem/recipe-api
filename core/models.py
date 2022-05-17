"""
Database models.
"""
from django.db import models
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
    id: str = models.UUIDField(
        default=uuid4,
        unique=True,
        primary_key=True,
        editable=False
    )
    email: str = models.EmailField(max_length=255, unique=True)
    name: str = models.CharField(max_length=255)
    is_active: bool = models.BooleanField(default=True)
    is_staff: bool = models.BooleanField(default=False)

    objects = UserManager()
    USERNAME_FIELD: str = 'email'
