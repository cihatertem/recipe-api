from core.models import User as CustomUser
from django.contrib.auth import get_user_model


def create_user(
        email: str = 'user@example.com',
        password: str = 'testpass123') -> CustomUser:
    """
    Create and return a new user.
    """
    User: CustomUser = get_user_model()
    return User.objects.create_user(
        email=email,
        password=password
    )
