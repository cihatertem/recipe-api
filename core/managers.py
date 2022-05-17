"""
Model Managers.
"""
from django.contrib.auth.models import BaseUserManager, User


class UserManager(BaseUserManager):
    """
    Manager for users.
    """

    def create_user(
            self,
            email: str,
            password: str | bool = None,
            **extra_fields
    ) -> User:
        """
        Create, save and return an user.
        """
        if not email or email is None:
            raise ValueError('User must have an email address.')
        user: User = self.model(
            email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        email: str,
        password: str,
    ) -> User:
        """
        Create and return a new superuser.
        """
        user: User = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
