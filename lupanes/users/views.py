from typing import Any
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model

from lupanes.users.forms import AuthForm, CustomerForm
from lupanes.users.mixins import ManagerAuthMixin
from lupanes.users import get_customers_group

User = get_user_model()


class CustomerCreateView(ManagerAuthMixin, CreateView):
    template_name = "users/user_form.html"
    form_class = CustomerForm
    success_url = reverse_lazy("lupanes:customer-list")

    def form_valid(self, form: CustomerForm) -> HttpResponse:
        response = super().form_valid(form)
        form.instance.groups.add(get_customers_group())
        return response


class CustomerProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "users/user_profile.html"

    def get_object(self, queryset=None):
        return self.request.user


class CustomerListView(FormView):
    template_name = "users/customer_list.html"
    form_class = AuthForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if context["form"].is_valid():
            context["object_list"] = User.objects.filter(groups__name="neveras")

        return context

    def form_valid(self, form: Any) -> HttpResponse:
        return self.form_invalid(form)
