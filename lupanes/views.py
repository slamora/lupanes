from typing import Any, Dict

from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, FormView

from lupanes.forms import CustomerAuthForm, DeliveryNoteCreateForm
from lupanes.models import Customer, DeliveryNote


class DeliveryNoteCreateView(CreateView):
    form_class = DeliveryNoteCreateForm
    model = DeliveryNote
    success_url = reverse_lazy("lupanes:deliverynote-new")

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        customer_id = self.request.session.get("customer_id")
        try:
            self.customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self) -> Dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["customer"] = self.customer
        return kwargs


class CustomerLoginView(FormView):
    form_class = CustomerAuthForm
    template_name = "lupanes/customer_login.html"
    success_url = reverse_lazy("lupanes:deliverynote-new")

    def form_valid(self, form: Any) -> HttpResponse:
        self.request.session["customer_id"] = form.customer_id
        return super().form_valid(form)
