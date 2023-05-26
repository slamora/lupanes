from django.contrib.auth.mixins import UserPassesTestMixin


CUSTOMERS_GROUP = "neveras"

MANAGERS_GROUP = "tienda"


class CustomerAuthMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and user.groups.filter(name=CUSTOMERS_GROUP).exists()


class ManagerAuthMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and user.groups.filter(name=MANAGERS_GROUP).exists()
