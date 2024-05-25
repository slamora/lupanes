import decimal

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as ContribUserManager
from django.db import models
from django.db.models.functions import Lower
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from lupanes import utils
from lupanes.users import CUSTOMERS_GROUP, MANAGERS_GROUP
from lupanes.users.validators import CustomUnicodeUsernameValidator


class UserManager(ContribUserManager):
    def get_active_customers(self):
        return self.filter(is_active=True, groups__name="neveras").order_by(Lower('username'))


class User(AbstractUser):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.

    Username and password are required. Other fields are optional.
    """

    username_validator = CustomUnicodeUsernameValidator()

    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )

    objects = UserManager()

    @property
    def is_customer(self):
        return self.groups.filter(name=CUSTOMERS_GROUP).exists()

    @property
    def is_manager(self):
        return self.groups.filter(name=MANAGERS_GROUP).exists()

    @cached_property
    def current_balance(self):
        if not self.is_customer:
            return

        balance = utils.search_nevera_balance(self.username)

        try:
            balance = decimal.Decimal(balance.replace(",", "."))
        except decimal.InvalidOperation:
            pass

        return balance
