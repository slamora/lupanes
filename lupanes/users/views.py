from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views.generic import CreateView, DetailView, FormView

from lupanes.users import get_customers_group
from lupanes.users.forms import AuthForm, CustomerForm
from lupanes.users.mixins import ManagerAuthMixin

User = get_user_model()


class CustomerCreateView(ManagerAuthMixin, CreateView):
    template_name = "users/user_form.html"
    form_class = CustomerForm
    success_url = reverse_lazy("lupanes:customer-list")

    def form_valid(self, form: CustomerForm) -> HttpResponse:
        response = super().form_valid(form)
        form.instance.groups.add(get_customers_group())

        self.send_password_reset_email(form.instance)
        return response

    def send_password_reset_email(self, new_user):
        new_user.set_unusable_password()
        new_user.save()

        uidb64 = urlsafe_base64_encode(force_bytes(new_user.pk))
        token = default_token_generator.make_token(new_user)

        reset_path = reverse_lazy('users:password_reset_confirm', kwargs={
            'uidb64': uidb64,
            'token': token
        })
        reset_link = self.request.build_absolute_uri(reset_path)
        new_user.email_user(
            subject="Establece tu contraseña | App Albaranes Lupierra",
            message=f"Hola! Establece tu contraseña para acceder a la app usando el siguiente enlace: {reset_link}",
        )


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
