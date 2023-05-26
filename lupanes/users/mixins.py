from django.contrib.auth.mixins import UserPassesTestMixin


class CustomerAuthMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and user.groups.filter(name="neveras").exists()
