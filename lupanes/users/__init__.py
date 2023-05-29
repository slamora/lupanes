CUSTOMERS_GROUP = "neveras"

MANAGERS_GROUP = "tienda"


def get_customers_group():
    from django.contrib.auth.models import Group
    return Group.objects.get(name=CUSTOMERS_GROUP)
