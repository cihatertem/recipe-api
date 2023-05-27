"""
Dabase models' managers.
"""

from django.contrib.auth.models import BaseUserManager, AbstractBaseUser


class UserManager(BaseUserManager):
    """Custom manager for Custom User model."""

    def create_user(
            self, email: str, password: str | None = None, **extra_fields
    ) -> AbstractBaseUser:
        """Create, save and return a new user based Custom User Model."""

        if email is None or not email:
            raise ValueError("User must have en email address.")

        normalized_email = self.normalize_email(email)
        user: AbstractBaseUser = self.model(
            email=normalized_email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(
            self, email: str, password: str | None = None, **extra_fields
    ) -> AbstractBaseUser:
        """Create, save and return a new super user based Custom User Model."""
        user = self.create_user(email, password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user
