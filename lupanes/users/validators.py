from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class CustomUnicodeUsernameValidator(validators.RegexValidator):
    # NOTE: this regex allow initial & final spaces, you are advised to trim it!
    regex = r'^[\w.@+\- ]+$'
    message = _(
        "Enter a valid username. This value may contain only letters, "
        "numbers, and @/./+/-/_ characters."
    )
    flags = 0
