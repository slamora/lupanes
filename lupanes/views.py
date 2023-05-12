from typing import Any, Dict
from django.db.models import QuerySet

from django.utils import timezone
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, DeleteView, FormView, UpdateView

from lupanes.forms import CustomerAuthForm, DeliveryNoteCreateForm
from lupanes.models import DeliveryNote
from lupanes.mixins import CustomerAuthMixin


class CustomerLoginView(FormView):
    form_class = CustomerAuthForm
    template_name = "lupanes/customer_login.html"
    success_url = reverse_lazy("lupanes:deliverynote-new")

    def form_valid(self, form: Any) -> HttpResponse:
        self.request.session["customer_id"] = form.customer_id
        return super().form_valid(form)


class DeliveryNoteCreateView(CustomerAuthMixin, CreateView):
    form_class = DeliveryNoteCreateForm
    model = DeliveryNote
    success_url = reverse_lazy("lupanes:deliverynote-new")

    def get_form_kwargs(self) -> Dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["customer"] = self.customer
        return kwargs

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        context["deliverynotes_today"] = DeliveryNote.objects.filter(
            customer=self.customer, date__date=today,
        )
        return context


class DeliveryNoteUpdateView(CustomerAuthMixin, UpdateView):
    model = DeliveryNote
    fields = ["product", "quantity"]
    success_url = reverse_lazy("lupanes:deliverynote-new")

    def get_queryset(self) -> QuerySet[Any]:
        today = timezone.now().date()
        return DeliveryNote.objects.filter(customer=self.customer, date__date=today)


class DeliveryNoteDeleteView(CustomerAuthMixin, DeleteView):
    model = DeliveryNote
    success_url = reverse_lazy("lupanes:deliverynote-new")

    def get_queryset(self) -> QuerySet[Any]:
        today = timezone.now().date()
        return DeliveryNote.objects.filter(customer=self.customer, date__date=today)
