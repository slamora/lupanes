from django.contrib.auth.mixins import UserPassesTestMixin


CUSTOMERS_GROUP = "neveras"

MANAGERS_GROUP = "tienda"


# TODO(@slamora): move this methods to custom user model!!!!
class LupierraBaseAuth(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        user.is_customer = user.groups.filter(name=CUSTOMERS_GROUP).exists()
        user.is_manager = user.groups.filter(name=MANAGERS_GROUP).exists()


class CustomerAuthMixin(LupierraBaseAuth):
    def test_func(self):
        super().test_func()
        user = self.request.user
        return user.is_authenticated and user.is_customer


class ManagerAuthMixin(LupierraBaseAuth):
    def test_func(self):
        super().test_func()
        user = self.request.user
        return user.is_authenticated and user.is_manager
