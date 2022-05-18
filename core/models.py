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
