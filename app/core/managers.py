"""
Dabase models' managers.
"""

from django.contrib.auth.models import BaseUserManager, AbstractBaseUser


class UserManager(BaseUserManager):
    """Cusom manager for Custom User model."""

    def create_user(
            self, email: str, password: str | None = None, **extra_fields
    ) -> AbstractBaseUser:
        """Create, save and return a new user based Custom User Model."""
        user: AbstractBaseUser = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user
