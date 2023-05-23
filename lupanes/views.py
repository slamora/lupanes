import calendar
from decimal import Decimal
from typing import Any, Dict

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import DetailView, ListView, RedirectView
from django.views.generic.edit import (CreateView, DeleteView, FormView,
                                       UpdateView)

from lupanes import helpers
from lupanes.forms import CustomerAuthForm, DeliveryNoteCreateForm
from lupanes.mixins import CustomerAuthMixin
from lupanes.models import Customer, DeliveryNote, Product


class CustomerLoginView(FormView):
    form_class = CustomerAuthForm
    template_name = "lupanes/customer_login.html"
    success_url = reverse_lazy("lupanes:deliverynote-new")

    def form_valid(self, form: Any) -> HttpResponse:
        self.request.session["customer_id"] = form.customer_id
        return super().form_valid(form)


class CustomerLogoutView(RedirectView):
    pattern_name = "lupanes:customer-login"

    def get_redirect_url(self, *args, **kwargs):
        try:
            del self.request.session["customer_id"]
        except KeyError:
            pass
        return super().get_redirect_url(*args, **kwargs)


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


class DeliveryNoteListView(LoginRequiredMixin, ListView):
    model = DeliveryNote

    def get_queryset(self) -> QuerySet[Any]:
        value = self.request.GET.get("month")
        self.month = helpers.clean_month(value)

        return DeliveryNote.objects.filter(
            date__date__year=self.month.year,
            date__date__month=self.month.month,
        )

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        choices = {
            i: calendar.month_name[i]
            for i in range(1, today.month + 1)
        }

        context.update({
            "month": self.month,
            "choices": choices,
        })
        return context


class DeliveryNoteSummaryView(LoginRequiredMixin, ListView):
    template_name = "lupanes/deliverynote_summary.html"

    def get_queryset(self) -> QuerySet[Any]:
        value = self.request.GET.get("month")
        self.period = helpers.clean_month(value)

        qs = Customer.objects.filter(is_active=True)
        for customer in qs:
            customer.total = Decimal(0)
            notes = customer.deliverynote_set.filter(
                date__date__year=self.period.year,
                date__date__month=self.period.month,
            )
            for note in notes:
                customer.total += note.amount()

        return qs

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["period"] = self.period
        return context


class ProductAjaxView(DetailView):
    model = Product

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> JsonResponse:
        obj = self.get_object()
        data = {
            "pk": obj.pk,
            "name": obj.name,
            "price": obj.get_price_on(),
            "unit": {
                "name": obj.unit,
                "accept_decimals": obj.unit_accept_decimals(),
            }
        }
        return JsonResponse(data=data)
