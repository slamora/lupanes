from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView

from lupanes.users.forms import CustomerForm
from lupanes.users.mixins import ManagerAuthMixin
from lupanes.users import get_customers_group


class CustomerCreateView(ManagerAuthMixin, CreateView):
    template_name = "users/user_form.html"
    form_class = CustomerForm
    success_url = reverse_lazy("lupanes:customer-list")

    def form_valid(self, form: CustomerForm) -> HttpResponse:
        response = super().form_valid(form)
        form.instance.groups.add(get_customers_group())
        return response
