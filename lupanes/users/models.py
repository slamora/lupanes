from django.contrib.auth.models import AbstractUser

from lupanes.users.validators import CustomUnicodeUsernameValidator


class User(AbstractUser):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.

    Username and password are required. Other fields are optional.
    """

    username_validator = CustomUnicodeUsernameValidator()
